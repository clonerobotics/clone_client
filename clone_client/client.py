from __future__ import annotations

import asyncio
import logging
from socket import gethostname
from time import time
from types import TracebackType
from typing import Any, AsyncIterable, Coroutine, Dict, Optional, Sequence, Type

from typing_extensions import deprecated

from clone_client.config import CONFIG
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

LOGGER = logging.getLogger(__name__)


class Client:
    """Client for sending commands and requests to the controller and state."""

    def __init__(
        self,
        server: str = gethostname(),
        address: Optional[str] = None,
    ) -> None:
        self.server = server
        self.address = address

        self.controller_tunnel: ControllerClient
        self.state_tunnel: StateStoreReceiverClient

        self._ordering: Dict[str, int] = {}
        self._ordering_rev: Dict[int, str] = {}

    async def _get_controller(self) -> ControllerClient:
        if not self.address:
            controller_address, controller_port = await Discovery(
                self.server,
                CONFIG.communication.controller_service,
            ).discover()
        else:
            controller_address, controller_port = (
                self.address,
                CONFIG.communication.controller_service.default_port,
            )

        return ControllerClient(f"{controller_address}:{controller_port}", ControllerClientConfig())

    async def _get_state(self) -> StateStoreReceiverClient:
        if not self.address:
            state_address, state_port = await Discovery(
                self.server, CONFIG.communication.rcv_web_service
            ).discover()
        else:
            state_address, state_port = self.address, CONFIG.communication.rcv_web_service.default_port

        return StateStoreReceiverClient(f"{state_address}:{state_port}", StateStoreClientConfig())

    async def __aenter__(self) -> Client:
        self.controller_tunnel = await self._get_controller()
        self.state_tunnel = await self._get_state()

        await self.controller_tunnel.channel_ready()
        await self.state_tunnel.channel_ready()

        info = await self.get_system_info(reload=True)
        self._update_mappings(info)

        LOGGER.info("Client initialized and ready to use.")

        return self

    async def __aexit__(
        self, exc_type: Type[ClientError], value: ClientError, traceback: TracebackType
    ) -> None:
        await self.controller_tunnel.channel.__aexit__(exc_type, value, traceback)
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
            await asyncio.sleep(0.01)
            if time() - start >= timeout_ms / 1000:
                raise DesiredPressureNotAchievedError(timeout_ms)

            info = await self.get_waterpump_info()
            if info.pressure >= info.desired_pressure:
                break

    async def set_impulses(self, impulses: Sequence[Optional[float]]) -> None:
        """Send instruction to the controller to set any muscle into certain position"""
        await self.controller_tunnel.set_impulses(impulses)

    @deprecated('Use "set_impulses" instead.')
    async def set_muscls(self, muscles: Sequence[Optional[float]]) -> None:
        """Send instruction to the controller to set any muscle into certain position"""
        await self.set_impulses(muscles)

    async def set_pulses(self, pulses: Sequence[Pulse]) -> None:
        """Send instruction to the controller to set any muscle into certain position"""
        await self.controller_tunnel.set_pulses(pulses)

    async def set_pressures(self, pressures: Sequence[float]) -> None:
        """Send instruction to the controller to set any muscle into certain pressure."""
        await self.controller_tunnel.set_pressures(pressures)

    def stream_set_pressures(self, stream: AsyncIterable[Sequence[float]]) -> Coroutine[Any, Any, None]:
        """Send instruction to the controller to set any muscle into certain pressure."""
        return self.controller_tunnel.stream_set_pressures(stream)

    def subscribe_telemetry(self) -> AsyncIterable[TelemetryData]:
        """Send request to subscribe to muscle pressures updates."""
        return self.state_tunnel.subscribe_telemetry()

    async def get_telemetry(self) -> TelemetryData:
        """Send request to get the latest muscle pressures."""
        return await self.state_tunnel.get_telemetry()

    async def loose_all(self) -> None:
        """Send instruction to the controller to loose all muscles."""
        await self.controller_tunnel.loose_all()

    async def lock_all(self) -> None:
        """Send instruction to the controller to lock all muscles."""
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
        """Send request to get current information about waterpump metadata."""
        return await self.controller_tunnel.get_waterpump_info()

    async def get_system_info(self, reload: bool = False) -> SystemInfo:
        """
        Send request to get current information about hand metadata.

        `reload` - if True, force to reload hand info from the controller.
        """
        info: SystemInfo = await self.state_tunnel.get_system_info(reload)
        if reload:
            self._update_mappings(info)

        return info

    async def get_controller_config(self) -> ControllerRuntimeConfig:
        """Send request to get current configuration of the controller."""
        return await self.controller_tunnel.get_config()
