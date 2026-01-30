from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib

import numpy as np

from clone_client.dipole_estimation.joint_model import JointModelInfo


def _load_mapping(path: Path) -> dict:
    ext = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    if ext == ".json":
        obj = json.loads(text)
        if not isinstance(obj, dict):
            raise ValueError("JSON root must be an object")
        return obj

    if ext == ".toml":
        obj = tomllib.loads(text)
        if not isinstance(obj, dict):
            raise ValueError("TOML root must be a table")
        return obj

    raise ValueError(f"Unsupported extension {ext}; expected .json or .toml")


def _is_finite(a: np.ndarray) -> bool:
    return np.isfinite(a).all()


def _check_rot3(name: str, M: np.ndarray, *, eps_ortho: float = 1e-4, eps_det: float = 1e-3) -> list[str]:
    if M.shape != (3, 3):
        return [f"{name}: expected 3x3, got {M.shape}"]
    if not _is_finite(M):
        return [f"{name}: contains NaN/Inf"]

    c0, c1, c2 = M[:, 0], M[:, 1], M[:, 2]
    n0, n1, n2 = np.linalg.norm(c0), np.linalg.norm(c1), np.linalg.norm(c2)

    errs: list[str] = []
    if abs(n0 - 1.0) > eps_ortho:
        errs.append(f"{name}: col0 norm {n0:.6g} not ~1")
    if abs(n1 - 1.0) > eps_ortho:
        errs.append(f"{name}: col1 norm {n1:.6g} not ~1")
    if abs(n2 - 1.0) > eps_ortho:
        errs.append(f"{name}: col2 norm {n2:.6g} not ~1")

    d01, d02, d12 = float(c0 @ c1), float(c0 @ c2), float(c1 @ c2)
    if abs(d01) > eps_ortho:
        errs.append(f"{name}: col0·col1 {d01:.6g} not ~0")
    if abs(d02) > eps_ortho:
        errs.append(f"{name}: col0·col2 {d02:.6g} not ~0")
    if abs(d12) > eps_ortho:
        errs.append(f"{name}: col1·col2 {d12:.6g} not ~0")

    det = float(np.linalg.det(M))
    if abs(det - 1.0) > eps_det:
        errs.append(f"{name}: det {det:.6g} not ~ +1")

    return errs


def _check_vec3(name: str, v: np.ndarray) -> list[str]:
    if v.shape != (3,):
        return [f"{name}: expected shape (3,), got {v.shape}"]
    if not _is_finite(v):
        return [f"{name}: contains NaN/Inf"]
    return []


def _check_unit_vec3(name: str, v: np.ndarray, *, eps: float = 1e-3) -> list[str]:
    errs = _check_vec3(name, v)
    if errs:
        return errs
    n = float(np.linalg.norm(v))
    if n < 1e-12:
        return [f"{name}: zero vector"]
    if abs(n - 1.0) > eps:
        return [f"{name}: norm {n:.6g} not ~1"]
    return []


def check_joint_models(path: Path) -> tuple[bool, list[str]]:
    raw = _load_mapping(path)
    root = JointModelInfo.from_dict(raw)

    errors: list[str] = []
    if not root.joints:
        return False, ["No joints found in joint model set."]

    for joint_name, jm in root.joints.items():
        prefix = f"[{joint_name}]"

        frames = jm.joint_frames.frames
        if not frames:
            errors.append(f"{prefix} joint_frames.items is empty")

        for frame_name, jf in frames.items():
            errors += _check_rot3(f"{prefix} joint_frames.items.{frame_name}.R_wJ", jf.R_wJ.as_matrix())
            errors += _check_vec3(
                f"{prefix} joint_frames.items.{frame_name}.origin_w",
                np.asarray(jf.origin_w, float),
            )

        errors += _check_rot3(f"{prefix} sensor.frame_wS", jm.sensor.frame_wS.as_matrix())
        errors += _check_vec3(f"{prefix} sensor.origin_w", np.asarray(jm.sensor.origin_w, float))

        errors += _check_vec3(f"{prefix} magnet.origin_w", np.asarray(jm.magnet.origin_w, float))
        errors += _check_unit_vec3(
            f"{prefix} magnet.base_z_in_sensor",
            np.asarray(jm.magnet.base_z_in_sensor, float),
        )

        errors += _check_vec3(f"{prefix} dipole.position", np.asarray(jm.dipole.position, float))
        errors += _check_unit_vec3(f"{prefix} dipole.direction", np.asarray(jm.dipole.direction, float))

        sm = jm.mapping
        if not isinstance(sm.clone_sensor_id, str) or not sm.clone_sensor_id:
            errors.append(f"{prefix} mapping.clone_sensor_id missing/invalid")

        errors += _check_unit_vec3(
            f"{prefix} mapping.magnet_local_axis",
            np.asarray(sm.magnet_local_axis, float),
        )

        errors += _check_rot3(
            f"{prefix} mapping.r_corr",
            np.asarray(sm.r_corr.matrix, float),
        )

        bindings = jm.axis_to_hinge_bindings
        if not bindings.frames:
            errors.append(f"{prefix} axis_to_hinge_bindings.frames empty")

        for i, frame in enumerate(bindings.frames):
            if not isinstance(frame, dict):
                errors.append(f"{prefix} axis_to_hinge_bindings.frames[{i}] not a dict")
                continue
            for k, v in frame.items():
                if not isinstance(k, str) or not k:
                    errors.append(f"{prefix} axis_to_hinge_bindings.frames[{i}] has invalid key {k!r}")
                if not isinstance(v, str) or not v:
                    errors.append(
                        f"{prefix} axis_to_hinge_bindings.frames[{i}] has invalid value for {k!r}: {v!r}"
                    )

    return (len(errors) == 0), errors


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Validate JointModelInfo structure and numeric sanity (.json or .toml)."
    )
    ap.add_argument("path", type=Path, help="Path to joint model set (.json or .toml)")
    args = ap.parse_args()

    ok, errors = check_joint_models(args.path)

    if ok:
        print("OK: joint model set passed validation.")
        return

    print(f"FAIL: {len(errors)} issues found:")
    for e in errors:
        print(f"- {e}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
