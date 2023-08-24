from __future__ import annotations

import asyncio
import logging
from socket import gethostname
from time import time
from types import TracebackType
from typing import Dict, Optional, Set, Type, TypeVar

from clone_client.config import CommunicationService, CONFIG
from clone_client.controller.client import (
    configured_controller_client,
    ControllerClient,
)

# pylint: disable=E0611
from clone_client.controller.proto.supervisor_pb2 import (
    CompressorInfo as GRPCCompressorInfo,
)
from clone_client.discovery import Discovery
from clone_client.exceptions import (
    ClientError,
    DesiredPressureNotAchievedError,
    MissingConfigurationError,
)
from clone_client.state_store.config import STATE_STORE_CONFIG

# pylint: disable=E0611
from clone_client.state_store.proto.state_store_pb2 import HandInfo as GRPCHandInfo

# pylint: enable=E0611
from clone_client.state_store.rcv_client import (
    configured_subscriber,
    StateStoreReceiverClient,
)
from clone_client.types import (
    CompressorInfo,
    HandInfo,
    MuscleMovementsDataType,
    MuscleName,
    MusclePressuresDataType,
    ValveAddress,
)
from clone_client.utils import convert_grpc_instance_to_own_representation

# pylint: enable=E0611

LOGGER = logging.getLogger(__name__)

RequestData = TypeVar("RequestData")
ResponseData = TypeVar("ResponseData")
MappingValue = TypeVar("MappingValue")


class Client:
    """Client for sending commands and requests to the controller and state."""

    def __init__(
        self,
        server: str = gethostname(),
        controller_service: CommunicationService = CONFIG.communication.controller_service,
        state_service: Optional[CommunicationService] = STATE_STORE_CONFIG.publisher_web_service,
    ) -> None:
        self.server = server
        if state_service is None:
            raise MissingConfigurationError("state service")
        self.state_service: CommunicationService = state_service
        self.controller_service = controller_service

        self.controller_tunnel: ControllerClient
        self.state_tunnel: StateStoreReceiverClient

        self._ordering: Dict[MuscleName, int] = {}
        self._ordering_rev: Dict[int, MuscleName] = {}

    async def __aenter__(self) -> Client:
        controller_address, controller_port = await Discovery(
            self.server,
            self.controller_service,
        ).discover()

        state_address, state_port = await Discovery(self.server, self.state_service).discover()

        self.controller_tunnel = configured_controller_client(f"{controller_address}:{controller_port}")
        self.state_tunnel = configured_subscriber(f"{state_address}:{state_port}")

        await self.state_tunnel.channel_ready()
        await self.controller_tunnel.channel_ready()

        info = await self.get_hand_info(reload=True)
        self._update_mappings(info)

        LOGGER.info("Client initialized and ready to use.")

        return self

    async def __aexit__(
        self, exc_type: Type[ClientError], value: ClientError, traceback: TracebackType
    ) -> None:
        await self.controller_tunnel.channel.__aexit__(exc_type, value, traceback)
        await self.state_tunnel.channel.__aexit__(exc_type, value, traceback)

    @property
    def muscle_order(self) -> Dict[int, MuscleName]:
        """Get muscle order."""
        return self._ordering_rev

    @property
    def number_of_muscles(self) -> int:
        """Get number of muscles."""
        return len(self._ordering)

    def muscle_idx(self, name: str) -> int:
        """Get muscle index by name."""
        return self._ordering[name]

    def muscle_name(self, idx: int) -> str:
        """Get muscle name by index."""
        return self._ordering_rev[idx]

    def _update_mappings(self, info: HandInfo) -> None:
        for index, (_valve_id_packed, muscle_name) in enumerate(info.muscles.items()):
            self._ordering[muscle_name] = index
            self._ordering_rev[index] = muscle_name

    async def wait_for_desired_pressure(self, timeout_ms: int = 10000) -> None:
        """Block the execution until current compressor pressure is equal or more than desired pressure."""
        start = time()
        while True:
            await asyncio.sleep(0.01)
            if time() - start >= timeout_ms / 1000:
                raise DesiredPressureNotAchievedError(timeout_ms)

            info = await self.get_compressor_info()
            if info.pressure >= info.desired_pressure:
                break

    async def set_muscles(self, muscles: MuscleMovementsDataType) -> None:
        """Send instruction to the controller to set any muscle into certain position"""
        await self.controller_tunnel.set_muscles(muscles)

    async def get_pressures(self) -> MusclePressuresDataType:
        """Send request to get the latest muscle pressures."""
        pressures_record = await self.state_tunnel.get_pressures()
        return pressures_record[1]

    async def loose_all(self) -> None:
        """Send instruction to the controller to loose all muscles."""
        await self.controller_tunnel.loose_all()

    async def lock_all(self) -> None:
        """Send instruction to the controller to lock all muscles."""
        await self.controller_tunnel.lock_all()

    async def start_compressor(self) -> None:
        """Start compressor"""
        await self.controller_tunnel.start_compressor()

    async def stop_compressor(self) -> None:
        """Stop compressor"""
        await self.controller_tunnel.stop_compressor()

    async def set_compressor_pressure(self, pressure: float) -> None:
        """Stop compressor and set new desired pressure"""
        await self.controller_tunnel.set_compressor_pressure(pressure)

    async def get_valve_nodes(self, rediscover: bool = False) -> Set[ValveAddress]:
        """Send request to get discovered valve nodes."""
        return await self.controller_tunnel.get_nodes(rediscover)

    async def get_compressor_info(self) -> CompressorInfo:
        """Send request to get current information about compressor metadata."""
        compressor_info: GRPCCompressorInfo = await self.controller_tunnel.get_compressor_info()
        return convert_grpc_instance_to_own_representation(compressor_info, CompressorInfo)

    async def get_hand_info(self, reload: bool = False) -> HandInfo:
        """
        Send request to get current information about hand metadata.

        `reload` - if True, force to reload hand info from the controller.
        """
        hand_info: GRPCHandInfo = await self.state_tunnel.get_hand_info(reload)
        data = convert_grpc_instance_to_own_representation(hand_info, HandInfo)
        if reload:
            self._update_mappings(data)

        return data
