from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from clone_client.dipole_estimation.common import AxisToHingeBindings, SensorMapping


@dataclass(frozen=True)
class SiteMapping:
    sensor_site: str
    magnet_site: str

    def to_dict(self) -> dict:
        return {
            "sensor_site": self.sensor_site,
            "magnet_site": self.magnet_site,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SiteMapping":
        if not isinstance(d, dict):
            raise ValueError("SiteMapping payload must be an object")
        return cls(sensor_site=str(d["sensor_site"]), magnet_site=str(d["magnet_site"]))


@dataclass(frozen=True)
class JointConfig:
    name: str
    axis_to_hinge_bindings: AxisToHingeBindings
    sites: SiteMapping
    sensor_mapping: SensorMapping

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "axis_to_hinge_bindings": self.axis_to_hinge_bindings.to_dict(),
            "sites": self.sites.to_dict(),
            "sensor_mapping": self.sensor_mapping.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "JointConfig":
        if not isinstance(d, dict):
            raise ValueError("JointConfig payload must be an object")
        return cls(
            name=str(d["name"]),
            axis_to_hinge_bindings=AxisToHingeBindings.from_dict(d["axis_to_hinge_bindings"]),
            sites=SiteMapping.from_dict(d["sites"]),
            sensor_mapping=SensorMapping.from_dict(d["sensor_mapping"]),
        )

    def to_json(self, *, indent: int | None = None, sort_keys: bool = True) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=sort_keys, ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> "JointConfig":
        return cls.from_dict(json.loads(s))


@dataclass(frozen=True)
class AppConfig:
    joints: list[JointConfig]

    def to_dict(self) -> dict:
        return {"joints": [j.to_dict() for j in self.joints]}

    @classmethod
    def from_dict(cls, d: dict) -> "AppConfig":
        if not isinstance(d, dict) or "joints" not in d:
            raise ValueError("AppConfig payload must be an object with key 'joints'")
        joints_raw = d["joints"]
        if not isinstance(joints_raw, list):
            raise ValueError("AppConfig.joints must be a list")
        return cls(joints=[JointConfig.from_dict(j) for j in joints_raw])

    def to_json(self, *, indent: int | None = None, sort_keys: bool = True) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=sort_keys, ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> "AppConfig":
        return cls.from_dict(json.loads(s))

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
        text = self.to_json(indent=indent, sort_keys=sort_keys) + "\n"

        if not atomic:
            path.write_text(text, encoding="utf-8")
            return

        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    @classmethod
    def load(cls, path: str | Path) -> "AppConfig":
        path = Path(path)
        return cls.from_json(path.read_text(encoding="utf-8"))
