# async.sync
# This marks this file as to be automatically converted to sync version using async2sync.py

from typing import Annotated, AsyncIterable, Literal, Optional
import warnings

from google.protobuf.empty_pb2 import Empty  # pylint: disable=E0611
import numpy as np
import numpy.typing as npt
from scipy.spatial.transform import Rotation as R  # type: ignore

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

    def __init__(self, data: TelemetryData, client: "StateStoreClient") -> None:
        self._inner = data

        server_pose_estimation = {
            joint_name: R.from_quat([q.x, q.y, q.z, q.w])
            for joint_name, q in data.pose_estimation.pose_estimation.items()
        }
        if client._pose_estimator_maginterp is not None:
            mag_pose_estimation = client._pose_estimator_maginterp.get_rotations_dict(
                data.sensor_data.bfields
            )
            self._new_pose_estimation = {**server_pose_estimation, **mag_pose_estimation}
        else:
            self._new_pose_estimation = server_pose_estimation

        new_timestamp = data.time_since_start.ToNanoseconds() / 1000_000_000.0
        if client._last_pose_estimation is None:
            self._velocities = {joint_name: np.zeros(3) for joint_name in self._new_pose_estimation}
        else:
            # FIXME: short diff time in connection with no filtering (hence high wobbling of pose estimation)
            # brings to spurious high values of velocities
            # FIXME: below is a dumbfix for a situation where the same telemetry object is used
            # two times to create TelemetryDataExt (what caused ZeroDivisionError).
            # This one will be fixed with transferring calculation to the golem
            try:
                self._velocities = {
                    joint_name: (rnew * client._last_pose_estimation[joint_name].inv()).as_rotvec()
                    / (new_timestamp - client._last_telemetry_timestamp)
                    for joint_name, rnew in self._new_pose_estimation.items()
                }
            except ZeroDivisionError:
                warnings.warn(
                    "ZeroDivisionError happended during velocity calculation."
                    "Probably due to usage of the same TelemetryData object twice.",
                    RuntimeWarning,
                )
                self._velocities = {joint_name: np.zeros(3) for joint_name in self._new_pose_estimation}

        client._last_pose_estimation = self._new_pose_estimation
        client._last_telemetry_timestamp = new_timestamp

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
    def qpos(self) -> dict[str, R]:  # type: ignore[no-any-unimported]
        """Get mapping joint name -> joint rotation"""
        return self._new_pose_estimation

    @property
    def qvel(
        self,
    ) -> dict[str, np.ndarray[tuple[Literal[3]], np.dtype[np.double]]]:  # type: ignore[no-any-unimported]
        """Get vector of estimated joint velocities (as Vector3, rad/s)"""
        return self._velocities  # type: ignore[return-value]


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

        self._joints_axes_mapping: dict[str, list[str]] = {}

        self._pose_estimator_maginterp: Optional[PoseEstimatorMagInterpol] = None
        self._last_pose_estimation: Optional[dict[Annotated[str, "joint name"], R]] = None  # type: ignore
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
                self._joints_axes_mapping[joint_name] = []
                for axis_name, _ in joint.joint.axes.items():
                    self._joints_axes_mapping[joint_name].append(axis_name)
        if info.pose_estimation is not None and info.pose_estimation.HasField("maginterp"):
            self._pose_estimator_maginterp = PoseEstimatorMagInterpol.from_maginterp_info(
                info.pose_estimation,
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
    def jnt_to_axes(
        self,
    ) -> dict[str, list[str]]:
        """Get mapping from a joint name to names of its axes"""
        return self._joints_axes_mapping

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
