from __future__ import annotations

import argparse
import json
from pathlib import Path

import tomli_w


def _normalize(raw: object) -> dict:
    if isinstance(raw, dict) and "joints" in raw:
        return raw
    if isinstance(raw, list):
        return {"joints": raw}
    if isinstance(raw, dict) and "name" in raw:
        return {"joints": [raw]}
    raise ValueError("Expected {joints:[...]}, a list of joints, or a single joint object")


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert JSON config to TOML.")
    ap.add_argument("input_json", type=Path)
    ap.add_argument("output_toml", type=Path)
    args = ap.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    cfg = _normalize(data)

    for j in cfg.get("joints", []):
        sm = j.get("sensor_mapping")
        if isinstance(sm, dict) and "r_corr" not in sm and "R_corr" in sm:
            sm["r_corr"] = sm.pop("R_corr")

    args.output_toml.write_text(tomli_w.dumps(cfg), encoding="utf-8")


if __name__ == "__main__":
    main()
