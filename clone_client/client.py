from __future__ import annotations

from enum import auto, Flag
import ipaddress as ip
import logging
from pathlib import Path
from socket import gethostname
from time import time
from types import TracebackType
from typing import Any, AsyncIterable, Coroutine, Dict, Optional, Sequence, Type

from typing_extensions import deprecated

from clone_client.config import CommunicationService, CONFIG
from clone_client.controller.client import ControllerClient
from clone_client.controller.config import ControllerClientConfig
from clone_client.controller.proto.controller_pb2 import (
    WaterPumpInfo as GRPCWaterPumpInfo,
)
from clone_client.controller.proto.controller_pb2 import ControllerRuntimeConfig, Pulse
from clone_client.discovery import Discovery
from clone_client.exceptions import (
    ClientError,
    DesiredPressureNotAchievedError,
    IncorrectMuscleIndexError,
    IncorrectMuscleNameError,
)
from clone_client.state_store.client import StateStoreReceiverClient
from clone_client.state_store.config import StateStoreClientConfig
from clone_client.state_store.proto.state_store_pb2 import SystemInfo, TelemetryData
from clone_client.utils import async_busy_ticker

LOGGER = logging.getLogger(__name__)


class Client:
    # pylint: disable=too-many-public-methods
    """Client for sending commands and requests to the controller and state."""

    class TunnelsUsed(Flag):
        """Flag for selecting channels which are going to be used"""

        CONTROLLER = auto()
        STATE = auto()

    def __init__(
        self,
        server: str = gethostname(),
        address: Optional[str] = None,
        tunnels_used: TunnelsUsed = ~TunnelsUsed(0),
    ) -> None:
        self.server = server
        self.address = address
        self.tunnels_used = tunnels_used

        if Client.TunnelsUsed.CONTROLLER in tunnels_used:
            self.controller_tunnel: ControllerClient
        if Client.TunnelsUsed.STATE in tunnels_used:
            self.state_tunnel: StateStoreReceiverClient

        self._ordering: Dict[str, int] = {}
        self._ordering_rev: Dict[int, str] = {}

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

    def _update_mappings(self, info: SystemInfo) -> None:
        for index, valve_id_packed in enumerate(sorted(info.muscles.keys())):
            muscle_name = info.muscles[valve_id_packed]
            self._ordering[muscle_name] = index
            self._ordering_rev[index] = muscle_name

    async def wait_for_desired_pressure(self, timeout_ms: int = 10000) -> None:
        """Block the execution until current waterpump pressure is equal or more than desired pressure."""
        start = time()
        while True:
            async with async_busy_ticker(1 / 10):
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

    async def get_all_nodes(self, rediscover: bool = False) -> list[int]:
        """Returns list of node_ids present on both control and telemetry lines"""
        return list((await self.controller_tunnel.get_all_nodes(rediscover)).values)

    async def get_controlline_nodes(self, rediscover: bool = False) -> list[int]:
        """Returns list of node_ids present on control line"""
        return list((await self.controller_tunnel.get_controlline_nodes(rediscover)).values)

    async def get_telemetryline_nodes(self, rediscover: bool = False) -> list[int]:
        """Returns list of node_ids present on telemetry line"""
        return list((await self.controller_tunnel.get_telemetryline_nodes(rediscover)).values)

    async def get_controller_config(self) -> ControllerRuntimeConfig:
        """Get current configuration of the controller."""
        return await self.controller_tunnel.get_config()
