import asyncio

from clone_client.client import Client
from clone_client.kinematics.pose_estimator import PoseEstimator

DECIM_COEF = 5


async def print_pose_estimation(name, pose_stream):
    print(f"Starting pose estimator '{name}'")
    async for pose in pose_stream:
        print(f"New pose from '{name}': {pose}")
        print()


async def main() -> None:

    async with Client(address="/run/clone", tunnels_used=Client.TunnelsUsed.STATE) as client:
        # This is even simpler example, the only thing which is done over here is subscribing to telemetry.
        # May be used for telemetry debug.
        await client.get_system_info()
        pose_estimator_local = PoseEstimator(client.imu_mapping, client.subscribe_telemetry())

        print("Subscribing to pose estimation")

        await print_pose_estimation("Local", pose_estimator_local.pose_estimation_stream_euler())


asyncio.run(main())
