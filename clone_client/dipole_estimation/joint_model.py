from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R

from clone_client.dipole_estimation.common import (
    AxisToHingeBindings,
    RotSpec,
    SensorMapping,
)


def _vec3(v) -> np.ndarray:
    return np.array([v.x, v.y, v.z], dtype=float)


@dataclass(frozen=True)
class JointModelFrame:
    R_wJ: R
    origin_w: np.ndarray

    def to_dict(self) -> dict:
        return {
            "R_wJ": RotSpec.from_rotation(self.R_wJ).to_dict(),
            "origin_w": self.origin_w.tolist(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "JointModelFrame":
        return cls(
            R_wJ=RotSpec.from_dict(d["R_wJ"]).to_rotation(),
            origin_w=np.asarray(d["origin_w"], float),
        )

    @classmethod
    def from_proto(cls, p) -> "JointModelFrame":
        return cls(
            R_wJ=RotSpec.from_proto(p.r_wj).to_rotation(),
            origin_w=_vec3(p.origin_w),
        )


@dataclass(frozen=True)
class JointFrames:
    frames: dict[str, JointModelFrame]

    def to_dict(self) -> dict:
        return {"frames": {name: f.to_dict() for name, f in self.frames.items()}}

    @classmethod
    def from_dict(cls, d: dict) -> "JointFrames":
        return cls(frames={name: JointModelFrame.from_dict(payload) for name, payload in d["frames"].items()})

    @classmethod
    def from_proto(cls, p) -> "JointFrames":
        return cls(frames={name: JointModelFrame.from_proto(jf) for name, jf in p.frames.items()})


@dataclass(frozen=True)
class SensorGeometry:
    frame_wS: R
    origin_w: np.ndarray

    def to_dict(self) -> dict:
        return {
            "frame_wS": RotSpec.from_rotation(self.frame_wS).to_dict(),
            "origin_w": self.origin_w.tolist(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SensorGeometry":
        return cls(
            frame_wS=RotSpec.from_dict(d["frame_wS"]).to_rotation(),
            origin_w=np.asarray(d["origin_w"], float),
        )

    @classmethod
    def from_proto(cls, p) -> "SensorGeometry":
        return cls(
            frame_wS=RotSpec.from_proto(p.frame_wS).to_rotation(),
            origin_w=_vec3(p.origin_w),
        )


@dataclass(frozen=True)
class MagnetGeometry:
    origin_w: np.ndarray
    base_z_in_sensor: np.ndarray

    def to_dict(self) -> dict:
        return {
            "origin_w": self.origin_w.tolist(),
            "base_z_in_sensor": self.base_z_in_sensor.tolist(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MagnetGeometry":
        return cls(
            origin_w=np.asarray(d["origin_w"], float),
            base_z_in_sensor=np.asarray(d["base_z_in_sensor"], float),
        )

    @classmethod
    def from_proto(cls, p) -> "MagnetGeometry":
        return cls(
            origin_w=_vec3(p.origin_w),
            base_z_in_sensor=_vec3(p.base_z_in_sensor),
        )


@dataclass(frozen=True)
class DipoleSeed:
    position: np.ndarray
    direction: np.ndarray

    def to_dict(self) -> dict:
        return {"position": self.position.tolist(), "direction": self.direction.tolist()}

    @classmethod
    def from_dict(cls, d: dict) -> "DipoleSeed":
        return cls(
            position=np.asarray(d["position"], float),
            direction=np.asarray(d["direction"], float),
        )

    @classmethod
    def from_proto(cls, p) -> "DipoleSeed":
        return cls(position=_vec3(p.position), direction=_vec3(p.direction))


@dataclass(frozen=True)
class JointModel:
    joint_frames: JointFrames
    sensor: SensorGeometry
    magnet: MagnetGeometry
    dipole: DipoleSeed
    mapping: SensorMapping
    axis_to_hinge_bindings: AxisToHingeBindings

    def to_dict(self) -> dict:
        return {
            "joint_frames": self.joint_frames.to_dict(),
            "sensor": self.sensor.to_dict(),
            "magnet": self.magnet.to_dict(),
            "dipole": self.dipole.to_dict(),
            "mapping": self.mapping.to_dict(),
            "axis_to_hinge_bindings": self.axis_to_hinge_bindings.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "JointModel":
        return cls(
            joint_frames=JointFrames.from_dict(d["joint_frames"]),
            sensor=SensorGeometry.from_dict(d["sensor"]),
            magnet=MagnetGeometry.from_dict(d["magnet"]),
            dipole=DipoleSeed.from_dict(d["dipole"]),
            mapping=SensorMapping.from_dict(d["mapping"]),
            axis_to_hinge_bindings=AxisToHingeBindings.from_dict(d["axis_to_hinge_bindings"]),
        )

    @classmethod
    def from_proto(cls, p) -> "JointModel":
        return cls(
            joint_frames=JointFrames.from_proto(p.joint_frames),
            sensor=SensorGeometry.from_proto(p.sensor),
            magnet=MagnetGeometry.from_proto(p.magnet),
            dipole=DipoleSeed.from_proto(p.dipole),
            mapping=SensorMapping.from_proto(p.mapping),
            axis_to_hinge_bindings=AxisToHingeBindings.from_proto(p.axis_to_hinge_bindings),
        )

    def to_json(self, *, indent: int | None = None, sort_keys: bool = True) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=sort_keys, ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> "JointModel":
        return cls.from_dict(json.loads(s))


@dataclass(frozen=True)
class JointModelInfo:
    joints: dict[str, JointModel]

    def to_dict(self) -> dict:
        return {"joints": {k: v.to_dict() for k, v in self.joints.items()}}

    @classmethod
    def from_dict(cls, d: dict) -> "JointModelInfo":
        if not isinstance(d, dict) or "joints" not in d:
            raise ValueError("JointModelInfo payload must be a dict with key 'joints'")
        return cls(joints={name: JointModel.from_dict(jm) for name, jm in d["joints"].items()})

    def save(
        self,
        path: str | Path,
        *,
        indent: int = 2,
        sort_keys: bool = True,
        atomic: bool = False,
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(self.to_dict(), indent=indent, sort_keys=sort_keys, ensure_ascii=False) + "\n"

        if not atomic:
            path.write_text(text, encoding="utf-8")
            return

        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    @classmethod
    def load(cls, path: str | Path) -> "JointModelInfo":
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)


def joint_model_info_from_proto(p) -> dict[str, JointModel]:
    """Convert JointModelInfo proto to: joint_name -> JointModel."""
    return {name: JointModel.from_proto(jm) for name, jm in p.joints.items()}
