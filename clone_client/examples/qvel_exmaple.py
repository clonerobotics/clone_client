import asyncio
from os import getenv

from scipy.spatial.transform import Rotation

from clone_client.client import Client
from clone_client.pose_estimation.pose_estimator import MagInterpolConfig

# hardcoded for example
JOINT_NAME = "r-index-pip"


async def main() -> None:
    address = getenv("GOLEM_ADDRESS", "127.0.0.1")
    async with Client(
        address=address,
        tunnels_used=Client.TunnelsUsed.STATE,
        additional_config=Client.Config(maginterp_config=MagInterpolConfig(filter_avg_samples=16)),
    ) as client:
        async for tele_ext in client.state_store.telemetry_stream_extend(
            client.state_store.subscribe_telemetry()
        ):
            # take current position of a joint (scipy Rotation) and its velocity (3d vec as np array)
            joint_pos_curr = tele_ext.qpos[JOINT_NAME]
            joint_vel_curr = tele_ext.qvel[JOINT_NAME]

            # DT is telemetry period, hardcoded, but could be derived by comparing consequtive `tele_ext.raw.time_since_start`
            # for finger station it is set to 8ms
            dt = 0.008

            # forecast next position (in next sample)
            joint_pos_diff = joint_vel_curr * dt
            joint_pos_next = Rotation.from_rotvec(joint_pos_diff) * joint_pos_curr

            print(joint_pos_next.as_quat())


asyncio.run(main())
