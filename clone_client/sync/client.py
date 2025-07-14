from __future__ import annotations

from enum import auto, Flag
import ipaddress as ip
import logging
from pathlib import Path
from time import time
from types import TracebackType
from typing import Annotated, Dict, Iterable, Optional, Sequence, Type

from typing_extensions import deprecated

from clone_client.config import CommunicationService, CONFIG
from clone_client.controller.config import ControllerClientConfig
from clone_client.controller.sync.client import ControllerClient
from clone_client.exceptions import (
    ClientError,
    DesiredPressureNotAchievedError,
    IncorrectMuscleIndexError,
    IncorrectMuscleNameError,
)
from clone_client.proto.controller_pb2 import ControllerRuntimeConfig, Pulse
from clone_client.proto.controller_pb2 import WaterPumpInfo as GRPCWaterPumpInfo
from clone_client.proto.hardware_driver_pb2 import (
    BusDevice,
    PinchValveCommands,
    PinchValveControl,
)
from clone_client.proto.state_store_pb2 import (
    ImuMappingModel,
    JointType,
    SystemInfo,
    TelemetryData,
)
from clone_client.state_store.config import StateStoreClientConfig
from clone_client.state_store.sync.client import StateStoreReceiverClient
from clone_client.utils import precise_interval

LOGGER = logging.getLogger(__name__)


class Client:
    # pylint: disable=too-many-public-methods, too-many-instance-attributes
    """Client for sending commands and requests to the controller and state."""

    class TunnelsUsed(Flag):
        """Flag for selecting channels which are going to be used"""

        CONTROLLER = auto()
        STATE = auto()

    def __init__(
        self,
        address: str,
        tunnels_used: TunnelsUsed = ~TunnelsUsed(0),
    ) -> None:
        self.address = address
        self.tunnels_used = tunnels_used

        if Client.TunnelsUsed.CONTROLLER in tunnels_used:
            self.controller_tunnel: ControllerClient
        if Client.TunnelsUsed.STATE in tunnels_used:
            self.state_tunnel: StateStoreReceiverClient

        self._ordering: Dict[str, int] = {}
        self._ordering_rev: Dict[int, str] = {}

        self._imu_mapping_id: Dict[Annotated[int, "node_id"], ImuMappingModel] = {}
        self._imu_idx_to_imudata: Dict[Annotated[int, "idx"], ImuMappingModel] = {}
        # both dicts below return idx basing on sorting by node id
        self._imu_ordering_by_name: Dict[Annotated[str, "name"], Annotated[int, "idx"]] = {}
        self._imu_ordering_by_id: Dict[Annotated[int, "node_id"], Annotated[int, "idx"]] = {}

        self._qpos_to_joint_name: Dict[Annotated[int, "qpos_nr"], Annotated[str, "Joint name"]] = {}
        self._joint_name_to_qpos: Dict[Annotated[str, "Joint name"], Annotated[int, "qpos_nr"]] = {}

    def _create_socket_str(self, service: CommunicationService) -> str:
        try:
            ip.ip_address(self.address)  # test whether valid ip
            service_address, service_port = (
                self.address,
                service.default_port,
            )
            socket_str = f"{service_address}:{service_port}"
        except ValueError as e:
            LOGGER.debug("Passed address is not a net address, trying to use unix-socket")
            socket_path = Path(self.address) / Path(service.default_unix_sock_name)
            if not socket_path.is_socket():
                raise ValueError(f"Selected path ({socket_path}) does not point to a unix-socket") from e
            socket_str = f"unix://{socket_path}"

        LOGGER.debug(socket_str)
        return socket_str

    def _get_controller(self) -> ControllerClient:
        socket_str = self._create_socket_str(CONFIG.communication.controller_service)
        return ControllerClient(socket_str, ControllerClientConfig())

    def _get_state(self) -> StateStoreReceiverClient:
        socket_str = self._create_socket_str(CONFIG.communication.rcv_web_service)
        return StateStoreReceiverClient(socket_str, StateStoreClientConfig())

    def __enter__(self) -> Client:
        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            self.controller_tunnel = self._get_controller()
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            self.state_tunnel = self._get_state()

        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            self.controller_tunnel.channel_ready()
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            self.state_tunnel.channel_ready()

        if Client.TunnelsUsed.STATE in self.tunnels_used:
            info = self.get_system_info(reload=True)
            self._update_mappings(info)

        LOGGER.info("Client initialized and ready to use.")

        return self

    def __exit__(self, exc_type: Type[ClientError], value: ClientError, traceback: TracebackType) -> None:
        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            self.controller_tunnel.channel.__exit__(exc_type, value, traceback)
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            self.state_tunnel.channel.__exit__(exc_type, value, traceback)

    @property
    def muscle_order(self) -> Dict[int, str]:
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
    def number_of_imus(self) -> int:
        """Get number of IMUs"""
        return len(self._imu_mapping_id)

    def imu_index_by_name(self, name: str) -> int:
        """Get IMU index by name."""
        return self._imu_ordering_by_name[name]

    def imu_index_by_id(self, node_id: int) -> int:
        """Get IMU index by id."""
        return self._imu_ordering_by_id[node_id]

    def imu_name(self, idx: int) -> str:
        """Get IMU name by index."""
        return self._imu_idx_to_imudata[idx].name

    def imu_id(self, idx: int) -> int:
        """Get IMU id by index."""
        return self._imu_idx_to_imudata[idx].node_id

    def imu_order(self) -> Dict[int, ImuMappingModel]:
        """Get IMU order."""
        return self._imu_idx_to_imudata

    def imu_info(self, node_id: int) -> ImuMappingModel:
        """Get IMU info for id."""
        return self._imu_mapping_id[node_id]

    @property
    def imu_mapping(self) -> dict[Annotated[int, "node_id"], ImuMappingModel]:
        """Property giving access to an IMU mapping currently used by the client.
        Should not be mutated.
        """
        return self._imu_mapping_id

    @property
    def qpos_to_jnt_mapping(self) -> dict[Annotated[int, "qpos_nr"], Annotated[str, "Joint name"]]:
        """Get mapping from position in qpos vector to joint name.
        Note: 3-axes joints are prepended by an "{x, y, z}_" suffix
        for subsequent axes, e.g. 5 -> x_humerus.r, 6 -> y_humerus.r, 7 -> z_humerus.r
        """
        return self._qpos_to_joint_name

    @property
    def jnt_to_qpos_mapping(self) -> dict[Annotated[str, "Joint name"], Annotated[int, "qpos_nr"]]:
        """Get mapping from a joint name to its qpos. It is reverse of qpos_to_jnt_mapping"""
        return self._joint_name_to_qpos

    def _update_mappings(self, info: SystemInfo) -> None:
        for index, valve_id_packed in enumerate(sorted(info.muscles.keys())):
            muscle_name = info.muscles[valve_id_packed]
            self._ordering[muscle_name] = index
            self._ordering_rev[index] = muscle_name
        for joint in info.joints:
            name = joint.name
            jtype = joint.jtype
            qpos = joint.qpos_nr
            if jtype == JointType.DOF1:
                self._qpos_to_joint_name[qpos] = name
            elif jtype == JointType.DOF3:
                self._qpos_to_joint_name[qpos] = f"x_{name}"
                self._qpos_to_joint_name[qpos + 1] = f"y_{name}"
                self._qpos_to_joint_name[qpos + 2] = f"z_{name}"
        self._joint_name_to_qpos = {name: qpos for qpos, name in self._qpos_to_joint_name.items()}

    def wait_for_desired_pressure(self, timeout_ms: int = 10000) -> None:
        """Block the execution until current waterpump pressure is equal or more than desired pressure."""
        start = time()
        interval = precise_interval(1 / 10, precision=0.5)
        while True:
            next(interval)
            if time() - start >= timeout_ms / 1000:
                raise DesiredPressureNotAchievedError(timeout_ms)

            info = self.get_waterpump_info()
            if info.pressure >= info.desired_pressure:
                break

    def set_impulses(self, impulses: Sequence[Optional[float]]) -> None:
        """Set muscles into certain position for a certain time."""
        self.controller_tunnel.set_impulses(impulses)

    @deprecated('Use "set_impulses" instead.')
    def set_muscles(self, muscles: Sequence[Optional[float]]) -> None:
        """Set muscles into certain position for a certain time."""
        self.set_impulses(muscles)

    def set_pulses(self, pulses: Sequence[Pulse]) -> None:
        """Start pulses (timed oscilations) on muscles."""
        self.controller_tunnel.set_pulses(pulses)

    def set_pressures(self, pressures: Sequence[float]) -> None:
        """Set muscles into certain pressure."""
        self.controller_tunnel.set_pressures(pressures)

    def stream_set_pressures(self, stream: Iterable[Sequence[float]]) -> None:
        """Start a stream with muscle pressure updates to the controller."""
        return self.controller_tunnel.stream_set_pressures(stream)

    def send_pinch_valve_control(
        self, node_id: int, control_mode: PinchValveControl.ControlMode.ValueType, value: int
    ) -> None:
        """Send control to selected pinch valve"""
        self.controller_tunnel.send_pinch_valve_control(node_id, control_mode, value)

    def send_many_pinch_valve_control(self, data: dict[int, PinchValveControl]) -> None:
        """Send mass control to all pinch valves"""
        self.controller_tunnel.send_many_pinch_valve_control(data)

    def stream_many_pinch_valve_control(self, stream: Iterable[dict[int, PinchValveControl]]) -> None:
        """Stream mass control to all pinch valves"""
        self.controller_tunnel.stream_many_pinch_valve_control(stream)

    def send_pinch_valve_command(
        self,
        node_id: int,
        command: PinchValveCommands.ValueType,
    ) -> None:
        """Send ON/OFF or VBOOST_ON/OFF command to a selected pinch valve"""
        self.controller_tunnel.send_pinch_valve_command(node_id, command)

    def send_many_pinch_valve_command(self, commands: dict[int, PinchValveCommands.ValueType]) -> None:
        """Send ON/OFF or VBOOST_ON/OFF command to many selected pinch valves"""
        self.controller_tunnel.send_many_pinch_valve_command(commands)

    def subscribe_telemetry(self) -> Iterable[TelemetryData]:
        """Subscribe to muscle pressures updates."""
        return self.state_tunnel.subscribe_telemetry()

    def get_telemetry(self) -> TelemetryData:
        """Get current telemetry data."""
        return self.state_tunnel.get_telemetry()

    def loose_all(self) -> None:
        """Loose all muscles (deflate)."""
        self.controller_tunnel.loose_all()

    def lock_all(self) -> None:
        """Lock all muscles (stop any update to the muscles)."""
        self.controller_tunnel.lock_all()

    def start_waterpump(self) -> None:
        """Start waterpump"""
        self.controller_tunnel.start_waterpump()

    def stop_waterpump(self) -> None:
        """Stop waterpump"""
        self.controller_tunnel.stop_waterpump()

    def set_waterpump_pressure(self, pressure: float) -> None:
        """Stop waterpump and set new desired pressure"""
        self.controller_tunnel.set_waterpump_pressure(pressure)

    def get_waterpump_info(self) -> GRPCWaterPumpInfo:
        """Get current information about waterpump metadata."""
        return self.controller_tunnel.get_waterpump_info()

    def get_system_info(self, reload: bool = False) -> SystemInfo:
        """
        Get current information about hand metadata.

        `reload` - if True, force to reload hand info from the controller.
        """
        info: SystemInfo = self.state_tunnel.get_system_info(reload)
        if reload:
            self._update_mappings(info)

        return info

    def ping(self) -> None:
        """Check if server is responding"""
        self.state_tunnel.ping()
        self.controller_tunnel.ping()

    def get_nodes(self) -> dict[str, list[BusDevice]]:
        """Returns list of devices per bus"""
        return {
            bus_name: list(devices.nodes)
            for bus_name, devices in self.controller_tunnel.get_nodes().nodes.items()
        }

    def get_controller_config(self) -> ControllerRuntimeConfig:
        """Get current configuration of the controller."""
        return self.controller_tunnel.get_config()

    def subscribe_pose_vector(self) -> Iterable[Sequence[float]]:
        """Subscribe to muscle pressures updates."""
        return self.state_tunnel.subscribe_pose_vector()
