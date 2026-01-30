from __future__ import annotations

from scipy.spatial.transform import Rotation as R

from clone_client.dipole_estimation.joint_model import JointModel
from clone_client.proto.state_store_pb2 import PoseEstimationData

FrameName = str
JointName = str

FrameRotMap = dict[FrameName, R]
AllFrameRots = dict[JointName, FrameRotMap]


def _quat_wxyz_to_rotation(w: float, x: float, y: float, z: float) -> R:
    """Convert quaternion [w, x, y, z] to scipy Rotation."""
    return R.from_quat([w, x, y, z], scalar_first=True)


def _resolve_joint_and_frame(
    key: str,
    joint_models: dict[JointName, JointModel],
) -> tuple[JointName, FrameName] | None:
    """
    Resolve a pose key into `(joint_name, frame_name)` for accessing `joint_models[joint_name]`
    and selecting a joint frame within that model.

    Canonical pose keys emitted by dipole estimation are always:
      - "joint::frame"

    For convenience, this function also accepts the shorthand form:
      - "joint"

    Shorthand semantics:
      - "joint" resolves to (joint_name="joint", frame_name="joint")
      - This only works if the joint model contains a frame whose name is exactly the joint name.

    Notes:
      - Frame names originate from the statics/config under:
          joints.<joint_name>.joint_frames.frames.<frame_name>
      - In MuJoCo-generated models (see `build_joint_models_from_mujoco`), frames are typically named:
          f"{joint_name}_frame{frame_idx}"
        so the shorthand form ("joint") will usually NOT resolve unless you explicitly create a frame
        named exactly `joint_name`.

    Returns:
      - (joint_name, frame_name) if `joint_name` exists in `joint_models`
      - None if `joint_name` is unknown
    """
    if "::" in key:
        joint_name, frame_name = key.split("::", 1)
        if joint_name not in joint_models:
            return None
        return joint_name, frame_name

    joint_name = key
    if joint_name not in joint_models:
        return None
    return joint_name, joint_name


def pose_msg_to_frame_rots(
    pose: PoseEstimationData,
    joint_models: dict[JointName, JointModel],
) -> AllFrameRots:
    out: AllFrameRots = {}

    for key, quat_msg in pose.pose_estimation.items():
        rot = _quat_wxyz_to_rotation(quat_msg.w, quat_msg.x, quat_msg.y, quat_msg.z)

        resolved = _resolve_joint_and_frame(key, joint_models)
        if resolved is None:
            continue

        joint_name, frame_name = resolved
        out.setdefault(joint_name, {})[frame_name] = rot

    return out


def _extract_xyz_euler(r: R) -> tuple[float, float, float]:
    """Return intrinsic XYZ Euler angles in radians."""
    ex, ey, ez = r.as_euler("XYZ", degrees=False)
    return ex, ey, ez


def frame_rots_to_hinge_angles(
    joint_models: dict[JointName, JointModel],
    frame_rots: AllFrameRots,
) -> dict[str, float]:
    """
    Applies each joint's control_bindings to its available frames.

    Note: This keeps the behavior of mapping binding frame index
    to a frame selected by sorted frame names.
    """
    result: dict[str, float] = {}

    for joint_name, js in joint_models.items():
        rots_for_joint = frame_rots.get(joint_name)
        if not rots_for_joint:
            continue

        frame_names_sorted = sorted(js.joint_frames.frames.keys())
        bindings = js.axis_to_hinge_bindings.frames

        for frame_idx, frame_axes in enumerate(bindings):
            if frame_idx >= len(frame_names_sorted):
                break

            frame_name = frame_names_sorted[frame_idx]
            r_frame = rots_for_joint.get(frame_name)
            if r_frame is None:
                continue

            ex, ey, ez = _extract_xyz_euler(r_frame)

            for axis_id, control_name in frame_axes.items():
                if not axis_id:
                    continue

                axis = axis_id[0].lower()
                if axis == "x":
                    angle = ex
                elif axis == "y":
                    angle = ey
                elif axis == "z":
                    angle = ez
                else:
                    continue

                result[str(control_name)] = float(angle)

    return result


def pose_msg_to_control_angles(
    pose: PoseEstimationData,
    joint_models: dict[JointName, JointModel],
) -> dict[str, float]:
    return frame_rots_to_hinge_angles(joint_models, pose_msg_to_frame_rots(pose, joint_models))
