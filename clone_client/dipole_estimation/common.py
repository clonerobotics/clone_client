from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.spatial.transform import Rotation as R

# -----------------------------------------------------------------------------
# Defs
# -----------------------------------------------------------------------------

_DEFAULT_RCORR_Y_180 = [
    [-1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, -1.0],
]


@dataclass(frozen=True)
class Mat3Rot:
    matrix: list[list[float]]  # 3x3

    def to_dict(self) -> dict:
        mat = np.asarray(self.matrix, dtype=float)
        if mat.shape != (3, 3):
            raise ValueError("matrix must be 3x3")
        return {"matrix": mat.tolist()}

    @classmethod
    def from_dict(cls, d: dict) -> "Mat3Rot":
        mat = np.asarray(d["matrix"], dtype=float)
        if mat.shape != (3, 3):
            raise ValueError("matrix must be 3x3")
        return cls(matrix=mat.tolist())

    def to_rotation(self) -> R:
        return R.from_matrix(np.asarray(self.matrix, dtype=float))

    @classmethod
    def from_rotation(cls, r: R) -> "Mat3Rot":
        return cls(matrix=r.as_matrix().tolist())

    @classmethod
    def default_y_180(cls) -> "Mat3Rot":
        return cls(matrix=[row[:] for row in _DEFAULT_RCORR_Y_180])

    @classmethod
    def from_proto_optional(cls, mat3) -> "Mat3Rot | None":
        """
        Mat3 is {col0?: Vec3, col1?: Vec3, col2?: Vec3}. Treat missing/None columns as absent.
        """
        if mat3 is None:
            return None

        c0 = getattr(mat3, "col0", None)
        c1 = getattr(mat3, "col1", None)
        c2 = getattr(mat3, "col2", None)
        if c0 is None or c1 is None or c2 is None:
            return None

        v0 = np.array([c0.x, c0.y, c0.z], dtype=float)
        v1 = np.array([c1.x, c1.y, c1.z], dtype=float)
        v2 = np.array([c2.x, c2.y, c2.z], dtype=float)

        mat = np.column_stack((v0, v1, v2))
        if mat.shape != (3, 3):
            raise ValueError("proto Mat3 did not form a 3x3 matrix")
        return cls(matrix=mat.tolist())

    @classmethod
    def from_proto_required(cls, mat3) -> "Mat3Rot":
        out = cls.from_proto_optional(mat3)
        if out is None:
            raise ValueError("required Mat3 missing/invalid in proto")
        return out

    @classmethod
    def from_proto(cls, mat3) -> "Mat3Rot | None":
        return cls.from_proto_required(mat3)


RcorrSpec = Mat3Rot
RotSpec = Mat3Rot


@dataclass(frozen=True)
class SensorMapping:
    clone_sensor_id: str
    magnet_local_axis: tuple[float, float, float] = (0.0, 0.0, 1.0)
    sensor_magnet_inversion: bool = False
    r_corr: RcorrSpec = field(default_factory=RcorrSpec.default_y_180)  # never None

    def to_dict(self) -> dict:
        return {
            "clone_sensor_id": self.clone_sensor_id,
            "magnet_local_axis": list(map(float, self.magnet_local_axis)),
            "sensor_magnet_inversion": bool(self.sensor_magnet_inversion),
            "r_corr": self.r_corr.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SensorMapping":
        if not isinstance(d, dict):
            raise ValueError("SensorMapping payload must be a dict")

        axis = tuple(map(float, d.get("magnet_local_axis", (0.0, 0.0, 1.0))))
        inv = bool(d.get("sensor_magnet_inversion", False))

        rc_payload = d.get("r_corr", d.get("R_corr"))
        r_corr = RcorrSpec.default_y_180() if rc_payload is None else RcorrSpec.from_dict(rc_payload)

        return cls(
            clone_sensor_id=str(d["clone_sensor_id"]),
            magnet_local_axis=axis,
            sensor_magnet_inversion=inv,
            r_corr=r_corr,
        )

    @classmethod
    def from_proto(cls, p) -> "SensorMapping":
        axis = (
            float(p.magnet_local_axis.x),
            float(p.magnet_local_axis.y),
            float(p.magnet_local_axis.z),
        )

        mat3 = getattr(p, "r_corr", None)
        r_corr = RcorrSpec.from_proto_optional(mat3) or RcorrSpec.default_y_180()

        return cls(
            clone_sensor_id=p.clone_sensor_id,
            magnet_local_axis=axis,
            sensor_magnet_inversion=bool(p.sensor_magnet_inversion),
            r_corr=r_corr,
        )


@dataclass(frozen=True)
class AxisToHingeBindings:
    frames: list[dict[str, str]]

    @classmethod
    def from_dict(cls, raw) -> "AxisToHingeBindings":
        if isinstance(raw, dict):
            return cls(frames=[{str(k): str(v) for k, v in raw.items()}])

        if isinstance(raw, list):
            frames: list[dict[str, str]] = []
            for frame in raw:
                if not isinstance(frame, dict):
                    raise TypeError("Each control_bindings frame must be a dict")
                frames.append({str(k): str(v) for k, v in frame.items()})
            return cls(frames=frames)

        raise TypeError(f"axis_to_hinge_bindings must be dict or list[dict], got {type(raw)}")

    def to_dict(self):
        return self.frames

    @classmethod
    def from_proto(cls, frames) -> "AxisToHingeBindings":
        raw_frames = [dict(frame.axis_to_hinge_bindings) for frame in frames]
        return cls.from_dict(raw_frames)
