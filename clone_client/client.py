from __future__ import annotations

from dataclasses import dataclass
from enum import auto, Flag
import ipaddress as ip
import logging
from pathlib import Path
from socket import gethostname
from time import time
from types import TracebackType
from typing import (
    Annotated,
    Any,
    AsyncIterable,
    Coroutine,
    Dict,
    Optional,
    Sequence,
    Type,
)

from typing_extensions import deprecated

from clone_client.config import CommunicationService, CONFIG
from clone_client.controller.client import ControllerClient
from clone_client.controller.config import ControllerClientConfig
from clone_client.discovery import Discovery
from clone_client.exceptions import (
    ClientError,
    DesiredPressureNotAchievedError,
    IncorrectMuscleIndexError,
    IncorrectMuscleNameError,
)
from clone_client.pose_estimation.pose_estimator import PoseEstimatorMagInterpol
from clone_client.proto.controller_pb2 import ControllerRuntimeConfig, Pulse
from clone_client.proto.controller_pb2 import WaterPumpInfo as GRPCWaterPumpInfo
from clone_client.proto.hardware_driver_pb2 import (
    BusDevice,
    HydraControlMessage,
    PinchValveCommands,
    PinchValveControl,
)
from clone_client.proto.state_store_pb2 import (
    SystemInfo,
    TelemetryData,
)
from clone_client.state_store.client import StateStoreReceiverClient
from clone_client.state_store.config import StateStoreClientConfig
from clone_client.utils import async_precise_interval

LOGGER = logging.getLogger(__name__)


class Client:
    # pylint: disable=too-many-public-methods, too-many-instance-attributes
    """Client for sending commands and requests to the controller and state."""

    class TunnelsUsed(Flag):
        """Flag for selecting channels which are going to be used"""

        CONTROLLER = auto()
        STATE = auto()

    @dataclass
    class Config:
        """Additional parameters for client"""

        maginterp_disable: bool = True
        maginterp_filter_avg_use: bool = True
        maginterp_filter_avg_samples: int = 8

    def __init__(
        self,
        server: str = gethostname(),
        address: Optional[str] = None,
        tunnels_used: TunnelsUsed = ~TunnelsUsed(0),
        additional_config: Config = Config(),
    ) -> None:
        self.server = server
        self.address = address
        self.tunnels_used = tunnels_used
        self._config = additional_config

        if Client.TunnelsUsed.CONTROLLER in tunnels_used:
            self.controller_tunnel: ControllerClient
        if Client.TunnelsUsed.STATE in tunnels_used:
            self.state_tunnel: StateStoreReceiverClient

        self._ordering: Dict[str, int] = {}
        self._ordering_rev: Dict[int, str] = {}

        self._qpos_to_joint_axis_name: Dict[
            Annotated[int, "qpos_nr"], Annotated[tuple[str, str], "Joint and axis names"]
        ] = {}
        self._joint_axis_name_to_qpos: Dict[
            Annotated[tuple[str, str], "Joint and axis names"], Annotated[int, "qpos_nr"]
        ] = {}

        self._pose_estimator_maginterp: Optional[PoseEstimatorMagInterpol] = None

    async def _create_socket_str(self, service: CommunicationService) -> str:
        if not self.address:
            service_address, service_port = await Discovery(self.server, service).discover()
            socket_str = f"{service_address}:{service_port}"
        else:
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

    async def _get_controller(self) -> ControllerClient:
        socket_str = await self._create_socket_str(CONFIG.communication.controller_service)
        return ControllerClient(socket_str, ControllerClientConfig())

    async def _get_state(self) -> StateStoreReceiverClient:
        socket_str = await self._create_socket_str(CONFIG.communication.rcv_web_service)
        return StateStoreReceiverClient(socket_str, StateStoreClientConfig())

    async def __aenter__(self) -> Client:
        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            self.controller_tunnel = await self._get_controller()
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            self.state_tunnel = await self._get_state()

        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            await self.controller_tunnel.channel_ready()
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            await self.state_tunnel.channel_ready()

        if Client.TunnelsUsed.STATE in self.tunnels_used:
            info = await self.get_system_info(reload=True)
            self._update_mappings(info)

        LOGGER.info("Client initialized and ready to use.")

        return self

    async def __aexit__(
        self, exc_type: Type[ClientError], value: ClientError, traceback: TracebackType
    ) -> None:
        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            await self.controller_tunnel.channel.__aexit__(exc_type, value, traceback)
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            await self.state_tunnel.channel.__aexit__(exc_type, value, traceback)

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

    def _update_mappings(self, info: SystemInfo) -> None:
        for muscle_name, muscle_info in info.muscles.items():
            self._ordering[muscle_name] = muscle_info.index
            self._ordering_rev[muscle_info.index] = muscle_name
        for joint_name, joint in info.joints.items():
            for axis_name, axis in joint.axes.items():
                self._qpos_to_joint_axis_name[axis.qpos_idx] = (joint_name, axis_name)
        self._joint_axis_name_to_qpos = {
            joint_axis_names: qpos for qpos, joint_axis_names in self._qpos_to_joint_axis_name.items()
        }
        if not self._config.maginterp_disable:
            if info.pose_estimation is None:
                raise RuntimeError("No pose estimator information was obtained from golem")
            if not info.pose_estimation.HasField("maginterp"):
                raise RuntimeError("No information on magnetic interpolator pose estimation obtained")
            self._pose_estimator_maginterp = PoseEstimatorMagInterpol.from_maginterp_info(
                info.pose_estimation,
                self._joint_axis_name_to_qpos,
                filter_avg_samples=self._config.maginterp_filter_avg_samples,
                filter_avg_use=self._config.maginterp_filter_avg_use,
            )

    async def wait_for_desired_pressure(self, timeout_ms: int = 10000) -> None:
        """Block the execution until current waterpump pressure is equal or more than desired pressure."""
        start = time()
        interval = async_precise_interval(1 / 10, 0.5)
        while True:
            await anext(interval)
            if time() - start >= timeout_ms / 1000:
                raise DesiredPressureNotAchievedError(timeout_ms)

            info = await self.get_waterpump_info()
            if info.pressure >= info.desired_pressure:
                break

    async def set_impulses(self, impulses: Sequence[Optional[float]]) -> None:
        """Set muscles into certain position for a certain time."""
        await self.controller_tunnel.set_impulses(impulses)

    @deprecated('Use "set_impulses" instead.')
    async def set_muscles(self, muscles: Sequence[Optional[float]]) -> None:
        """Set muscles into certain position for a certain time."""
        await self.set_impulses(muscles)

    async def set_pulses(self, pulses: Sequence[Pulse]) -> None:
        """Start pulses (timed oscilations) on muscles."""
        await self.controller_tunnel.set_pulses(pulses)

    async def set_pressures(self, pressures: Sequence[float]) -> None:
        """Set muscles into certain pressure."""
        await self.controller_tunnel.set_pressures(pressures)

    def stream_set_pressures(self, stream: AsyncIterable[Sequence[float]]) -> Coroutine[Any, Any, None]:
        """Start a stream with muscle pressure updates to the controller."""
        return self.controller_tunnel.stream_set_pressures(stream)

    async def send_pinch_valve_control(
        self, node_id: int, control_mode: PinchValveControl.ControlMode.ValueType, value: int
    ) -> None:
        """Send control to selected pinch valve"""
        await self.controller_tunnel.send_pinch_valve_control(node_id, control_mode, value)

    async def send_many_pinch_valve_control(self, data: dict[int, PinchValveControl]) -> None:
        """Send mass control to all pinch valves"""
        await self.controller_tunnel.send_many_pinch_valve_control(data)

    async def stream_many_pinch_valve_control(
        self, stream: AsyncIterable[dict[int, PinchValveControl]]
    ) -> None:
        """Stream mass control to all pinch valves"""
        await self.controller_tunnel.stream_many_pinch_valve_control(stream)

    async def send_pinch_valve_command(
        self,
        node_id: int,
        command: PinchValveCommands.ValueType,
    ) -> None:
        """Send ON/OFF or VBOOST_ON/OFF command to a selected pinch valve"""
        await self.controller_tunnel.send_pinch_valve_command(node_id, command)

    async def send_many_pinch_valve_command(self, commands: dict[int, PinchValveCommands.ValueType]) -> None:
        """Send ON/OFF or VBOOST_ON/OFF command to many selected pinch valves"""
        await self.controller_tunnel.send_many_pinch_valve_command(commands)

    async def send_hydra_control(
        self,
        node_id: int,
        control: HydraControlMessage,
    ) -> None:
        """Send control to selected Hydra valve"""
        await self.controller_tunnel.send_hydra_control(node_id, control)

    async def send_many_hydra_control(self, data: dict[int, HydraControlMessage]) -> None:
        """Send mass control to all Hydra valves"""
        await self.controller_tunnel.send_many_hydra_control(data)

    async def stream_many_hydra_control(self, stream: AsyncIterable[dict[int, HydraControlMessage]]) -> None:
        """Stream mass control to all Hydra valves"""
        await self.controller_tunnel.stream_many_hydra_control(stream)

    def subscribe_telemetry(self) -> AsyncIterable[TelemetryData]:
        """Subscribe to muscle pressures updates."""
        return self.state_tunnel.subscribe_telemetry()

    async def get_telemetry(self) -> TelemetryData:
        """Get current telemetry data."""
        return await self.state_tunnel.get_telemetry()

    async def loose_all(self) -> None:
        """Loose all muscles (deflate)."""
        await self.controller_tunnel.loose_all()

    async def lock_all(self) -> None:
        """Lock all muscles (stop any update to the muscles)."""
        await self.controller_tunnel.lock_all()

    async def start_waterpump(self) -> None:
        """Start waterpump"""
        await self.controller_tunnel.start_waterpump()

    async def stop_waterpump(self) -> None:
        """Stop waterpump"""
        await self.controller_tunnel.stop_waterpump()

    async def set_waterpump_pressure(self, pressure: float) -> None:
        """Stop waterpump and set new desired pressure"""
        await self.controller_tunnel.set_waterpump_pressure(pressure)

    async def get_waterpump_info(self) -> GRPCWaterPumpInfo:
        """Get current information about waterpump metadata."""
        return await self.controller_tunnel.get_waterpump_info()

    async def get_system_info(self, reload: bool = False) -> SystemInfo:
        """
        Get current information about hand metadata.

        `reload` - if True, force to reload hand info from the controller.
        """
        info: SystemInfo = await self.state_tunnel.get_system_info(reload)
        if reload:
            self._update_mappings(info)

        return info

    async def ping(self) -> None:
        """Check if server is responding"""
        await self.state_tunnel.ping()
        await self.controller_tunnel.ping()

    async def get_nodes(self) -> dict[str, list[BusDevice]]:
        """Returns list of devices per bus"""
        return {
            bus_name: list(devices.nodes)
            for bus_name, devices in (await self.controller_tunnel.get_nodes()).nodes.items()
        }

    async def get_controller_config(self) -> ControllerRuntimeConfig:
        """Get current configuration of the controller."""
        return await self.controller_tunnel.get_config()

    async def subscribe_angles(
        self, telemetry_stream: Optional[AsyncIterable[TelemetryData]] = None
    ) -> AsyncIterable[Sequence[float]]:
        """Subscribe pose estimation stream"""
        if self._pose_estimator_maginterp is None:
            raise RuntimeError(
                "Pose estimation not available with current setup."
                "Pose estimation is either disabled in client config"
                "or on golem server"
            )
        if telemetry_stream is None:
            telemetry_stream = self.subscribe_telemetry()
        async for telemetry in telemetry_stream:
            yield self._pose_estimator_maginterp.get_angles_vec(  # type: ignore
                telemetry.sensor_data.bfields, telemetry.pose_estimation
            )

    async def get_angles(self) -> Sequence[float]:
        """Get current pose estimation as a numpy array"""
        if self._pose_estimator_maginterp is None:
            raise RuntimeError(
                "Pose estimation not available with current setup."
                "Pose estimation is either disabled in client config"
                "or on golem server"
            )
        telemetry = await self.get_telemetry()
        return self._pose_estimator_maginterp.get_angles_vec(
            telemetry.sensor_data.bfields, telemetry.pose_estimation
        )
