from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib

import tomli_w

from clone_client.dipole_estimation.config import AppConfig
from clone_client.dipole_estimation.joint_model import JointModelInfo
from clone_client.dipole_estimation.mujoco_backend import MuJoCoBackend


def load_config(path: Path) -> AppConfig:
    ext = path.suffix.lower()
    if ext == ".toml":
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
        return AppConfig.from_dict(raw)
    if ext == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return AppConfig.from_dict(raw)
    raise ValueError(f"Unsupported config extension {ext}; expected .toml or .json")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate joint models from config + MuJoCo model.")
    ap.add_argument("--config", type=Path, required=True, help="Path to config (.toml or .json)")
    ap.add_argument("--model-xml", type=Path, required=True, help="Path to MuJoCo model XML")
    ap.add_argument(
        "--out", type=Path, default=Path("joint_models.json"), help="Output path (.json or .toml)"
    )
    ap.add_argument("--atomic", action="store_true", help="Atomic write (tmp + replace)")
    args = ap.parse_args()

    cfg = load_config(args.config)

    backend = MuJoCoBackend(str(args.model_xml), enable_viewer=False)
    joint_models_map = backend.build_joint_models(cfg)

    sf = JointModelInfo(joints=joint_models_map)

    out_ext = args.out.suffix.lower()
    if out_ext == ".json":
        sf.save(args.out, atomic=args.atomic)
        return

    if out_ext == ".toml":
        payload = sf.to_dict()
        text = tomli_w.dumps(payload) + "\n"
        if not args.atomic:
            args.out.write_text(text, encoding="utf-8")
        else:
            tmp = args.out.with_suffix(args.out.suffix + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(args.out)
        return

    raise ValueError(f"Unsupported output extension {out_ext}; expected .json or .toml")


if __name__ == "__main__":
    main()
