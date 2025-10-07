import asyncio
from os import getenv
from pprint import pprint

from clone_client.client import Client
from clone_client.pose_estimation.pose_estimator import (
    PoseEstimatorMagInterpol,
    rewrap_telemetry,
)


async def main():
    address = getenv("GOLEM_ADDRESS", "127.0.0.1")
    gauss_joint_mapping_path = getenv(
        "GAUSS_JOINT_MAP", "../pose_estimation/gaussrider_joint_mapping-example.toml"
    )
    interpol_mapping_path = getenv("INTERPOL_MAP", "../pose_estimation/magmap-righthand-example.json")
    pose_estimator = PoseEstimatorMagInterpol(interpol_mapping_path, gauss_joint_mapping_path, 16, True)
    async with Client(address=address, tunnels_used=Client.TunnelsUsed.STATE) as client:
        async for tele in client.subscribe_telemetry():
            pose_estimation = pose_estimator.get_angles_dict(rewrap_telemetry(tele))
            pprint(pose_estimation)


asyncio.run(main())
