from __future__ import annotations

import mujoco as mj
import numpy as np
from scipy.spatial.transform import Rotation as R

from clone_client.dipole_estimation.config import JointConfig
from clone_client.dipole_estimation.joint_model import (
    DipoleSeed,
    JointFrames,
    JointModel,
    JointModelFrame,
    MagnetGeometry,
    SensorGeometry,
)


def initial_guess_from_mid_rom(
    model: mj.MjModel,
    data: mj.MjData,
    sid: int,
    mid: int,
    R_corr: np.ndarray,
    axis_local: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Mid-ROM initializer (single pair):
    returns (c_rel0, u_rel0) in the SENSOR(+R_corr) frame.
    """
    qpos = data.qpos
    qpos[:] = model.qpos0

    # enums
    J_FREE = mj.mjtJoint.mjJNT_FREE
    J_BALL = mj.mjtJoint.mjJNT_BALL
    J_SLIDE = mj.mjtJoint.mjJNT_SLIDE
    J_HINGE = mj.mjtJoint.mjJNT_HINGE

    j_type = model.jnt_type
    j_limited = model.jnt_limited
    j_range = model.jnt_range
    j_qposadr = model.jnt_qposadr

    # mid for limited hinge/slide; normalize for ball/free
    for j in range(model.njnt):
        jt = j_type[j]
        adr = j_qposadr[j]
        if jt == J_HINGE or jt == J_SLIDE:
            if j_limited[j]:
                lo, hi = j_range[j, 0], j_range[j, 1]
                qpos[adr] = 0.5 * (lo + hi)
        elif jt == J_BALL:
            q = qpos[adr : adr + 4]
            n = float(np.linalg.norm(q))
            qpos[adr : adr + 4] = q / n if n > 0 else np.array([1, 0, 0, 0], float)
        elif jt == J_FREE:
            q = qpos[adr + 3 : adr + 7]
            n = float(np.linalg.norm(q))
            qpos[adr + 3 : adr + 7] = q / n if n > 0 else np.array([1, 0, 0, 0], float)

    mj.mj_forward(model, data)

    p_s = data.site_xpos[sid].copy()
    p_m = data.site_xpos[mid].copy()
    R_s = data.site_xmat[sid].reshape(3, 3).copy()
    R_m = data.site_xmat[mid].reshape(3, 3).copy()

    # world → sensor_corrected
    R_sensor_T = R_corr @ R_s.T

    r_world = p_m - p_s
    n_m_world = R_m @ axis_local

    c_rel0 = R_sensor_T @ r_world
    u_rel0 = R_sensor_T @ n_m_world

    nrm = float(np.linalg.norm(u_rel0))
    if nrm > 0:
        u_rel0 = u_rel0 / nrm
    else:
        u_rel0 = np.array([0, 0, 1.0], float)

    qpos[:] = model.qpos0
    mj.mj_forward(model, data)

    return c_rel0.astype(np.float32), u_rel0.astype(np.float32)


def _rcorr_from_cfg(sm) -> R | None:
    return R.from_matrix(np.asarray(sm.r_corr.matrix, float))


def build_midrom_seeds(model: mj.MjModel, data: mj.MjData, j: JointConfig) -> tuple[np.ndarray, np.ndarray]:
    sm = j.sensor_mapping

    sid = mj.mj_name2id(model, mj.mjtObj.mjOBJ_SITE, j.sites.sensor_site)
    mid = mj.mj_name2id(model, mj.mjtObj.mjOBJ_SITE, j.sites.magnet_site)

    if sid < 0 or mid < 0:
        # fallback seed if sites are missing
        return np.zeros(3, np.float32), np.array([0, 0, 1], np.float32)

    Rc = _rcorr_from_cfg(sm)
    axis_local = np.asarray(sm.magnet_local_axis, float)

    c0, u0 = initial_guess_from_mid_rom(model, data, sid, mid, Rc.as_matrix(), axis_local)
    return c0, u0


def _axis_world_from_joint(model: mj.MjModel, data: mj.MjData, jname: str) -> np.ndarray:
    jid = mj.mj_name2id(model, mj.mjtObj.mjOBJ_JOINT, jname)
    if jid < 0:
        raise KeyError(f"joint '{jname}' not found")
    bid = model.jnt_bodyid[jid]
    R_wB = data.xmat[bid].reshape(3, 3)
    a_B = model.jnt_axis[jid]
    a_W = R_wB @ a_B
    return a_W / (np.linalg.norm(a_W) + 1e-12)


def _origin_world_from_joint(model: mj.MjModel, data: mj.MjData, jname: str) -> np.ndarray:
    jid = mj.mj_name2id(model, mj.mjtObj.mjOBJ_JOINT, jname)
    if jid < 0:
        raise KeyError(f"joint '{jname}' not found")
    bid = model.jnt_bodyid[jid]
    R_wB = data.xmat[bid].reshape(3, 3)
    p_wB = data.xpos[bid]
    p_BJ = model.jnt_pos[jid]
    return p_wB + R_wB @ p_BJ


def _make_right_handed(X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> np.ndarray:
    X = X / (np.linalg.norm(X) + 1e-12)
    Y = Y - X * np.dot(X, Y)
    Y = Y / (np.linalg.norm(Y) + 1e-12)
    Z = np.cross(X, Y)
    Z = Z / (np.linalg.norm(Z) + 1e-12)
    Rw = np.column_stack((X, Y, Z))
    if np.linalg.det(Rw) < 0:
        Rw[:, 1] *= -1.0
    return Rw


def _frame_from_partial_axes(
    xW: np.ndarray | None, yW: np.ndarray | None, zW: np.ndarray | None
) -> np.ndarray:
    eps = 1e-12
    gZ = np.array([0.0, 0.0, 1.0])
    gX = np.array([1.0, 0.0, 0.0])

    def nrm(v: np.ndarray) -> np.ndarray:
        return v / (np.linalg.norm(v) + eps)

    if zW is not None:
        Z = nrm(zW)
        if xW is not None:
            X = xW - Z * np.dot(xW, Z)
            if np.linalg.norm(X) < 1e-10:
                X = (yW - Z * np.dot(yW, Z)) if (yW is not None) else (gX - Z * np.dot(gX, Z))
        else:
            X = (yW - Z * np.dot(yW, Z)) if (yW is not None) else (gX - Z * np.dot(gX, Z))
        X = nrm(X)
        Y = np.cross(Z, X)
        Y = nrm(Y)
        X = np.cross(Y, Z)
        X = nrm(X)
        Rw = np.column_stack((X, Y, Z))
        if np.linalg.det(Rw) < 0:
            Rw[:, 1] *= -1.0
        return Rw

    if (xW is not None) and (yW is not None):
        X = nrm(xW)
        Y = yW - X * np.dot(X, yW)
        Y = nrm(Y)
        Z = np.cross(X, Y)
        Z = nrm(Z)
        Rw = np.column_stack((X, Y, Z))
        if np.linalg.det(Rw) < 0:
            Rw[:, 1] *= -1.0
        return Rw

    if xW is not None:
        X = nrm(xW)
        helper = gZ if abs(np.dot(X, gZ)) < 0.9 else gX
        Y = helper - X * np.dot(helper, X)
        Y = nrm(Y)
        Z = np.cross(X, Y)
        Z = nrm(Z)
        return _make_right_handed(X, Y, Z)

    if yW is not None:
        Y = nrm(yW)
        helper = gZ if abs(np.dot(Y, gZ)) < 0.9 else gX
        X = helper - Y * np.dot(helper, Y)
        X = nrm(X)
        Z = np.cross(X, Y)
        Z = nrm(Z)
        return _make_right_handed(X, Y, Z)

    raise ValueError("At least one of xW/yW/zW must be provided.")


def _get_joint_frame_from_bindings(
    model: mj.MjModel,
    data: mj.MjData,
    bindings: dict[str, str],
) -> tuple[R, np.ndarray]:
    has_x = "x" in bindings and bindings["x"] is not None
    has_y = "y" in bindings and bindings["y"] is not None
    has_z = "z" in bindings and bindings["z"] is not None

    if not (has_x or has_y or has_z):
        raise KeyError("bindings must include at least one of 'x','y','z'.")

    xW = _axis_world_from_joint(model, data, bindings["x"]) if has_x else None
    yW = _axis_world_from_joint(model, data, bindings["y"]) if has_y else None
    zW = _axis_world_from_joint(model, data, bindings["z"]) if has_z else None

    R_wJ_mat = _frame_from_partial_axes(xW, yW, zW)

    if has_z:
        origin_joint = bindings["z"]
    elif has_x:
        origin_joint = bindings["x"]
    else:
        origin_joint = bindings["y"]

    p_wJ = _origin_world_from_joint(model, data, origin_joint)
    return R.from_matrix(R_wJ_mat), p_wJ


def _get_site_pose_world(model: mj.MjModel, data: mj.MjData, sname: str) -> tuple[R, np.ndarray]:
    sid = mj.mj_name2id(model, mj.mjtObj.mjOBJ_SITE, sname)
    if sid < 0:
        raise KeyError(f"site '{sname}' not found")
    R_wS = R.from_matrix(data.site_xmat[sid].reshape(3, 3))
    p_wS = np.asarray(data.site_xpos[sid], float)
    return R_wS, p_wS


def build_joint_models_from_mujoco(
    model: mj.MjModel,
    data: mj.MjData,
    cfg,
) -> dict[str, JointModel]:
    """
    Build `JointModel`s from a MuJoCo model/config, including joint-frame definitions used for pose keys.

    Frame naming:
      - Each joint may define multiple "frames" via `axis_to_hinge_bindings.frames`.
      - For each populated entry at index `frame_idx`, this builder emits a joint frame named:
          frame_name = f"{jc.name}_frame{frame_idx}"
      - These names become the `frame_name` component of the canonical dipole pose key:
          pose_key = f"{joint_name}::{frame_name}"
        Example:
          joint_name = "l-thumb-pip"
          frame_idx  = 0
          frame_name = "l-thumb-pip_frame0"
          pose_key   = "l-thumb-pip::l-thumb-pip_frame0"

    Implications:
      - Consumers should treat pose keys as "joint::frame" and should not assume a 1:1 joint->pose mapping.
      - If you want shorthand pose keys ("joint"), you must ensure a frame exists whose name equals `joint_name`.
        This builder does not create such a frame by default.

    Returns:
      - dict mapping `joint_name -> JointModel`, where `JointModel.joint_frames.frames` is keyed by `frame_name`.
    """
    models: dict[str, JointModel] = {}

    for jc in cfg.joints:
        jc: JointConfig

        frames_cfg = jc.axis_to_hinge_bindings.frames
        if not frames_cfg:
            raise ValueError(f"joint {jc.name} has no axis_to_hinge_bindings frames")

        joint_frames: dict[str, JointModel] = {}

        for frame_idx, frame_axes in enumerate(frames_cfg):
            if not frame_axes:
                continue

            basis_bindings: dict[str, str] = {}
            for axis_id, jname in frame_axes.items():
                if not axis_id:
                    continue
                base = axis_id[0].lower()
                if base in ("x", "y", "z"):
                    basis_bindings[base] = jname

            if not basis_bindings:
                continue

            R_wJ, origin_w = _get_joint_frame_from_bindings(model, data, basis_bindings)

            frame_name = f"{jc.name}_frame{frame_idx}"
            joint_frames[frame_name] = JointModelFrame(R_wJ=R_wJ, origin_w=origin_w)

        if not joint_frames:
            print(f"joint {jc.name} produced no joint_frames")

        sensor_R, sensor_p = _get_site_pose_world(model, data, jc.sites.sensor_site)
        magnet_R, magnet_p = _get_site_pose_world(model, data, jc.sites.magnet_site)

        r_corr = _rcorr_from_cfg(jc.sensor_mapping)
        sensor_R = sensor_R * r_corr

        z_world = magnet_R.as_matrix()[:, 2]
        base_z_in_sensor = sensor_R.inv().as_matrix() @ z_world
        base_z_in_sensor /= np.linalg.norm(base_z_in_sensor) + 1e-12

        c0, u0 = build_midrom_seeds(model, data, jc)

        jm = JointModel(
            joint_frames=JointFrames(frames=joint_frames),
            sensor=SensorGeometry(frame_wS=sensor_R, origin_w=sensor_p),
            magnet=MagnetGeometry(origin_w=magnet_p, base_z_in_sensor=base_z_in_sensor),
            dipole=DipoleSeed(position=c0, direction=u0),
            mapping=jc.sensor_mapping,
            axis_to_hinge_bindings=jc.axis_to_hinge_bindings,
        )
        models[jc.name] = jm

    return models
