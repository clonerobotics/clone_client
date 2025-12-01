from typing import Annotated, AsyncIterable, Optional

from google.protobuf.empty_pb2 import Empty  # pylint: disable=E0611
import numpy as np
import numpy.typing as npt

from clone_client.error_frames import handle_response
from clone_client.exceptions import IncorrectMuscleIndexError, IncorrectMuscleNameError
from clone_client.grpc_client import GRPCAsyncClient
from clone_client.pose_estimation.pose_estimator import (
    MagInterpolConfig,
    PoseEstimatorMagInterpol,
)
from clone_client.proto.data_types_pb2 import ErrorInfo, ErrorList
from clone_client.proto.state_store_pb2 import (
    SystemInfo,
    SystemInfoResponse,
    TelemetryData,
    TelemetryDataResponse,
)
from clone_client.proto.state_store_pb2_grpc import StateStoreReceiverGRPCStub
from clone_client.state_store.config import StateStoreClientConfig
from clone_client.utils import grpc_translated_async


class StateStoreClient(GRPCAsyncClient):
    """Client for receiving data from the state store."""

    def __init__(
        self, socket_address: str, config: StateStoreClientConfig, maginterpol_config: MagInterpolConfig
    ) -> None:
        super().__init__("StateStoreReceiver", socket_address)
        self.stub: StateStoreReceiverGRPCStub = StateStoreReceiverGRPCStub(self.channel)
        self._system_info: Optional[SystemInfo] = None
        self._config = config
        self._maginterpol_config = maginterpol_config

        self._ordering: dict[str, int] = {}
        self._ordering_rev: dict[int, str] = {}

        self._qpos_to_joint_axis_name: dict[
            Annotated[int, "qpos_nr"], Annotated[tuple[str, str], "Joint and axis names"]
        ] = {}
        self._joint_axis_name_to_qpos: dict[
            Annotated[tuple[str, str], "Joint and axis names"], Annotated[int, "qpos_nr"]
        ] = {}

        self._pose_estimator_maginterp: Optional[PoseEstimatorMagInterpol] = None

    @classmethod
    async def new(cls, socket_address: str, maginterpol_config: MagInterpolConfig) -> "StateStoreClient":
        """Create and initialize new `StateStoreClient` instance"""
        self = cls(socket_address, StateStoreClientConfig(), maginterpol_config)
        await self.channel_ready()
        return self

    async def subscribe_telemetry(self) -> AsyncIterable[TelemetryData]:
        """Subscribe to muscle pressures updates."""
        response: TelemetryDataResponse
        # timeout must be none to allow the client to wait indefinitely,
        # otherwise it crashes after said timeout
        async for response in self.stub.SubscribeTelemetry(Empty(), timeout=None):
            handle_response(response.response_data)
            yield response.data

    @grpc_translated_async()
    async def get_telemetry(self) -> TelemetryData:
        """Get current telemetry data."""
        response: TelemetryDataResponse = await self.stub.GetTelemetry(
            Empty(), timeout=self._config.continuous_rpc_timeout
        )
        handle_response(response.response_data)

        return response.data

    @grpc_translated_async()
    async def get_system_info(self, reload: bool = False) -> SystemInfo:
        """Send request to get the hand info."""
        if reload or not self._system_info:
            response: SystemInfoResponse = await self.stub.GetSystemInfo(
                Empty(), timeout=self._config.info_gathering_rpc_timeout
            )
            self._system_info = response.info

        return self._system_info

    @grpc_translated_async()
    async def ping(self) -> None:
        """Check if server is responding."""
        await self.stub.Ping(Empty(), timeout=self._config.info_gathering_rpc_timeout)

    @grpc_translated_async()
    async def get_errors(self) -> Optional[list[ErrorInfo]]:
        """Obtain list of state-store's errors from recent time"""
        response: ErrorList = await self.stub.GetErrors(Empty(), timeout=self._config.continuous_rpc_timeout)
        if response.HasField("errors_list"):
            return list(response.errors_list.errors)
        return None

    def _update_mappings(self, info: SystemInfo) -> None:
        for muscle_name, muscle_info in info.muscles.items():
            self._ordering[muscle_name] = muscle_info.index
            self._ordering_rev[muscle_info.index] = muscle_name
        if info.HasField("pose_estimation"):
            for joint_name, joint in info.pose_estimation.joints.items():
                for axis_name, axis in joint.joint.axes.items():
                    self._qpos_to_joint_axis_name[axis.qpos_idx] = (joint_name, axis_name)
            self._joint_axis_name_to_qpos = {
                joint_axis_names: qpos for qpos, joint_axis_names in self._qpos_to_joint_axis_name.items()
            }
        if not self._maginterpol_config.disable:
            if info.pose_estimation is None:
                raise RuntimeError("No pose estimator information was obtained from golem")
            if not info.pose_estimation.HasField("maginterp"):
                raise RuntimeError("No information on magnetic interpolator pose estimation obtained")
            self._pose_estimator_maginterp = PoseEstimatorMagInterpol.from_maginterp_info(
                info.pose_estimation,
                self._joint_axis_name_to_qpos,
                filter_avg_samples=self._maginterpol_config.filter_avg_samples,
                filter_avg_use=self._maginterpol_config.filter_avg_use,
            )

    async def subscribe_angles(
        self, telemetry_stream: Optional[AsyncIterable[TelemetryData]] = None
    ) -> AsyncIterable[npt.NDArray[np.float64]]:
        """Subscribe pose estimation stream"""
        if telemetry_stream is None:
            telemetry_stream = self.subscribe_telemetry()
        if self._pose_estimator_maginterp is None:
            async for telemetry in telemetry_stream:
                yield np.array(telemetry.pose_estimation)
        else:
            async for telemetry in telemetry_stream:
                yield self._pose_estimator_maginterp.get_angles_vec(
                    telemetry.sensor_data.bfields, telemetry.pose_estimation
                )

    async def get_angles(self) -> npt.NDArray[np.float64]:
        """Get current pose estimation as a numpy array"""
        telemetry = await self.get_telemetry()
        if self._pose_estimator_maginterp is None:
            return np.array(telemetry.pose_estimation)
        return self._pose_estimator_maginterp.get_angles_vec(
            telemetry.sensor_data.bfields, telemetry.pose_estimation
        )

    @property
    def muscle_order(self) -> dict[int, str]:
        """Get muscle order."""
        return self._ordering_rev

    @property
    def number_of_muscles(self) -> int:
        """Get number of muscles."""
        return len(self._ordering)

    def muscle_idx(self, name: str) -> int:
        """Get muscle index by name."""
        try:
            return self._ordering[name]
        except KeyError as err:
            raise IncorrectMuscleNameError(name) from err

    def muscle_name(self, idx: int) -> str:
        """Get muscle name by index."""
        try:
            return self._ordering_rev[idx]
        except KeyError as err:
            raise IncorrectMuscleIndexError(idx) from err

    @property
    def qpos_to_jnt_mapping(
        self,
    ) -> dict[Annotated[int, "qpos_nr"], Annotated[tuple[str, str], "Joint and axis names"]]:
        """Get mapping from position in qpos vector to joint and axis names tuple."""
        return self._qpos_to_joint_axis_name

    @property
    def jnt_to_qpos_mapping(
        self,
    ) -> dict[Annotated[tuple[str, str], "Joint and axis names"], Annotated[int, "qpos_nr"]]:
        """Get mapping from joint and axis names tuple to its qpos. It is reverse of qpos_to_jnt_mapping"""
        return self._joint_axis_name_to_qpos
