import argparse
import asyncio
import logging
import time
from types import ModuleType
from typing import Annotated, AsyncIterable, AsyncIterator, Optional, Sequence

import numpy as np
from scipy.spatial.transform import Rotation

from clone_client.discovery import AsyncThreadSafeEvent

try:
    import roboticstoolbox as rtb
except ImportError:
    rtb: Optional[ModuleType] = None  # roboticstoolbox is optional, only for Visualizer

from clone_client.client import Client
from clone_client.kinematics.tools import utils
from clone_client.kinematics.tools.visualization_tools.visualization_tools import (
    KinematicsVisualizer,
)
from clone_client.state_store.proto.state_store_pb2 import (
    IMUData,
    ImuMappingModel,
    TelemetryData,
)

L = logging.getLogger(__name__)

ROOT_ID = 0xFF

PoseEstimationRot = dict[Annotated[str, "IMU name"], Rotation]
PoseEstimationEuler = dict[
    Annotated[str, "IMU name"], Annotated[np.ndarray[tuple[3], np.dtype[np.float32]], "Euler angles"]
]
PoseEstimationQuat = dict[Annotated[str, "IMU name"], utils.Quaternion]


class PoseEstimator:
    """Class allowing user to obtain pose estimation - both directly from server
    and locally, deriving it from telemetry data.
    """

    def __init__(
        self,
        imu_mapping_id: dict[Annotated[int, "node_id"], ImuMappingModel],
        imu_stream: Optional[AsyncIterable[TelemetryData]] = None,
    ) -> None:
        super().__init__()
        self._imu_mapping = {node_id: imu_model.name for node_id, imu_model in imu_mapping_id.items()}
        self._imu_stream = imu_stream
        self._running = False
        L.debug("IMU mapping in PoseEstimator: %s", self._imu_mapping)

    async def _pose_estimation_stream(self, func):
        if self._imu_stream is None:
            raise RuntimeError(
                "Cannot run pose estimation stream because IMU stream was not passed into constructor"
            )
        if self._running:
            raise RuntimeError(
                "Streaming is already running and current implementation forbids to run"
                " two streams at the same time"
            )
        self._running = True
        async for tele_data in self._imu_stream:
            imu_data_seq = tele_data.imu
            yield func(imu_data_seq)

    async def pose_estimation_stream_rot(self) -> AsyncIterator[PoseEstimationRot]:
        """Asynchronous iterator allowing to wait and receive new pose-estimation data"""
        async for item in self._pose_estimation_stream(self.from_imu_data_seq_rot):
            yield item

    async def pose_estimation_stream_quat(self) -> AsyncIterator[PoseEstimationQuat]:
        """Asynchronous iterator allowing to wait and receive new pose-estimation data"""
        async for item in self._pose_estimation_stream(self.from_imu_data_seq_quat):
            yield item

    async def pose_estimation_stream_euler(self) -> AsyncIterator[PoseEstimationEuler]:
        """Asynchronous iterator allowing to wait and receive new pose-estimation data"""
        async for item in self._pose_estimation_stream(self.from_imu_data_seq_euler):
            yield item

    def from_imu_data_seq_rot(self, imu_data: Sequence[IMUData]) -> PoseEstimationRot:
        """Converts IMU data sequence received from the golem's telemetry to a dict
        from an IMU name to its rotation expressed as scipy's rotation
        """
        return {self._imu_mapping[item.node_id]: utils.rot_from_imu_data(item) for item in imu_data}

    def from_imu_data_seq_euler(self, imu_data: Sequence[IMUData], euler_type="ZYX") -> PoseEstimationEuler:
        """Converts IMU data sequence received from the golem's telemetry to a dict
        from an IMU name to its rotation expressed in the Euler's angles (by default ZYX intrinsic,
        for other types look at type strings in docs:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.as_euler.html
        """
        return {
            self._imu_mapping[item.node_id]: utils.rot_from_imu_data(item).as_euler(euler_type)
            for item in imu_data
        }

    def from_imu_data_seq_quat(self, imu_data: Sequence[IMUData]) -> PoseEstimationQuat:
        """Converts IMU data sequence received from the golem's telemetry to a dict
        from an IMU name to its rotation expressed as a quaternion.
        """
        return {self._imu_mapping[item.node_id]: utils.quat_from_imu_data(item) for item in imu_data}


class ArmPoseEstimatorVisualizer:
    """Class for visualization of hand movement basing on data from the PoseEstimator instance"""

    def __init__(self, address: str) -> None:
        if rtb is None:
            raise RuntimeError("EstimatorVisualizer cannot be used without RoboticsToolbox")
        self._client = Client(address=address, tunnels_used=Client.TunnelsUsed.STATE)
        self._hand_pose_estimator: PoseEstimator
        self._decimation_time_s = 0.1
        self._close_ev = AsyncThreadSafeEvent()

        hand_ets = (
            rtb.ET.Rz()
            * rtb.ET.Ry()
            * rtb.ET.Rx()
            * rtb.ET.tx(-0.5)
            * rtb.ET.Rz()
            * rtb.ET.Ry()
            * rtb.ET.Rx()
            * rtb.ET.tx(-0.5)
            * rtb.ET.Rz()
            * rtb.ET.Ry()
            * rtb.ET.Rx()
            * rtb.ET.tx(-0.1)
        )
        self._kv = KinematicsVisualizer(hand_ets, lambda _: self._close_ev.set())

        L.info("PrototypingVisualizer initialized")

    def main(self) -> None:
        """Blocking function running an event loop with main_task inside"""
        asyncio.run(self.main_task())

    async def _kill_task(self) -> None:
        await self._close_ev.wait()
        for task in asyncio.all_tasks():
            task.cancel()

    async def main_task(self) -> None:
        """Main task of the class, runs visualization of a hand and moves it accordingly
        to obtained arm pose estimation.
        """
        try:
            asyncio.create_task(self._kill_task())
            async with self._client:
                await self._client.get_system_info()
                self._hand_pose_estimator = PoseEstimator(
                    self._client.imu_mapping,
                    self._client.subscribe_telemetry(),
                )
                needed_angles = ["arm_r", "forearm_r", "hand_r"]
                last_time_s = time.time()
                async for pose in self._hand_pose_estimator.pose_estimation_stream_euler():
                    # decimation
                    L.debug("New telemetry")
                    curr_time_s = time.time()
                    if curr_time_s - last_time_s < self._decimation_time_s:
                        continue
                    last_time_s = curr_time_s
                    L.debug("New tele accepted: %s", pose)

                    q = [pose[name][i] for name in needed_angles for i in range(3)]
                    self._kv.update_plot(q)
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-a", "--address", help="IP or UNIX-socket address of a running golem system", default="/run/clone"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    L.info("Running test program")

    ArmPoseEstimatorVisualizer(args.address).main()
    L.info("Bye")
