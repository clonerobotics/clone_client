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


class TelemetryDataExt:
    # pylint: disable=W0212
    """NOTE: for deriving velocities this function uses and modifies
    internal, class-level state (shared by all `TelemetryDataExt` instances).
    NOTE: To get possibly best velocities approximation, this must be created
    with each telemetry value in turn, that is obtained from Golem.
    Best to use with a telemetry stream.
    """

    # velocity related global state
    # TBD: to avoid global state it may be benefitial to create
    # a class wrapping `TelemetryDataExt`, which would hold
    # that state
    _last_pose_estimation: Optional[npt.NDArray[np.double]] = None
    _last_telemetry_timestamp = 0.0

    def __init__(self, data: TelemetryData, client: "StateStoreClient") -> None:
        self._inner = data
        if client._pose_estimator_maginterp is not None:
            self._new_pose_estimation = client._pose_estimator_maginterp.get_angles_vec(
                data.sensor_data.bfields, data.pose_estimation
            )
        else:
            self._new_pose_estimation = np.array(data.pose_estimation)
        new_timestamp = data.time_since_start.ToNanoseconds() / 1000_000_000.0
        if TelemetryDataExt._last_pose_estimation is None:
            self._velocities = np.zeros_like(self._new_pose_estimation)
        else:
            self._velocities = (self._new_pose_estimation - TelemetryDataExt._last_pose_estimation) / (
                new_timestamp - TelemetryDataExt._last_telemetry_timestamp
            )
        TelemetryDataExt._last_pose_estimation = self._new_pose_estimation
        TelemetryDataExt._last_telemetry_timestamp = new_timestamp

    @property
    def raw(self) -> TelemetryData:
        """Access to inner raw `TelemetryData` structure.
        Useful when access to sensor data other then pressure
        is needed."""
        return self._inner

    @property
    def pressures(self) -> npt.NDArray[np.double]:
        """Get vector of pressures"""
        return np.array(self._inner.sensor_data.pressures)

    @property
    def qpos(self) -> npt.NDArray[np.double]:
        """Get vector of estimated joint angles."""
        return self._new_pose_estimation

    @property
    def qvel(self) -> ...:
        """Get vector of estimated joint velocities."""
        return self._velocities


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
        self._last_pose_estimation: Optional[npt.NDArray[np.double]] = None
        self._last_telemetry_timestamp = 0.0

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
            self._update_mappings(self._system_info)

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

    def telemetry_extend(self, telemetry_data: TelemetryData) -> TelemetryDataExt:
        """Wrap `TelemetryData` obtained from a Golem into an extension
        object, which facilitates obtaining joint pose and velocity estimation"""
        return TelemetryDataExt(telemetry_data, self)

    async def telemetry_stream_extend(
        self, telemetry_stream: AsyncIterable[TelemetryData]
    ) -> AsyncIterable[TelemetryDataExt]:
        """Wrap telemetry stream so that it returns `TelemetryDataExt`"""
        async for tele in telemetry_stream:
            yield TelemetryDataExt(tele, self)
