from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from os import getenv
import time

from clone_visualizer_client import ZmqClient

from clone_client.client import Client
from clone_client.dipole_estimation.dipole_quat_to_hinges import (
    pose_msg_to_control_angles,
)
from clone_client.dipole_estimation.joint_model import joint_model_info_from_proto


@dataclass(frozen=True)
class Args:
    address: str


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="Subscribe to telemetry and publish estimated joint angles.")
    parser.add_argument(
        "--address",
        default=getenv("GOLEM_ADDRESS", "192.168.99.102"),
        help="Golem address (default: env GOLEM_ADDRESS or 192.168.99.102).",
    )
    ns = parser.parse_args()
    return Args(address=str(ns.address))


def vsim_bone_name_to_normal(name: str) -> str:
    if name.endswith(("_r", "_l")):
        base, side = name.rsplit("_", 1)
        return f"{base}.{side}"
    return name


def normalize_payload_keys(payload: dict[str, float]) -> dict[str, float]:
    return {vsim_bone_name_to_normal(k): v for k, v in payload.items()}


async def run(address: str) -> None:
    vis = ZmqClient()
    vis.start()

    async with Client(address=address, tunnels_used=Client.TunnelsUsed.STATE) as client:
        system_info = await client.state_store.get_system_info()
        joint_models = joint_model_info_from_proto(system_info.joint_model_info)

        last_t = time.time()

        async for tele in client.state_store.subscribe_telemetry():
            now_t = time.time()

            angles = pose_msg_to_control_angles(tele.pose_estimation, joint_models)
            await vis.send_q_dict_from_name(normalize_payload_keys(angles))

            print(f"elapsed: {now_t - last_t:.4f}s")
            last_t = now_t


def main() -> None:
    args = parse_args()
    asyncio.run(run(args.address))


if __name__ == "__main__":
    main()
