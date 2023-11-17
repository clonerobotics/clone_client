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
    PressureGenInfo as GRPCPressureGenInfo,
)
from clone_client.discovery import Discovery
from clone_client.exceptions import (
    ClientError,
    DesiredPressureNotAchievedError,
    IncorrectMuscleIndexError,
    IncorrectMuscleNameError,
    MissingConfigurationError,
)
from clone_client.state_store.config import STATE_STORE_CONFIG

# pylint: disable=E0611
from clone_client.state_store.proto.state_store_pb2 import HandInfo as GRPCHandInfo

# pylint: enable=E0611
from clone_client.state_store.rcv_client import (
    configured_subscriber,
    StateStoreReceiverClient,
    TrackingRecord,
)
from clone_client.types import (
    HandInfo,
    MuscleMovementsDataType,
    MuscleName,
    MusclePressuresDataType,
    PressureGenInfo,
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

    def _update_mappings(self, info: HandInfo) -> None:
        for index, valve_id_packed in enumerate(sorted(info.muscles.keys())):
            muscle_name = info.muscles[valve_id_packed]
            self._ordering[muscle_name] = index
            self._ordering_rev[index] = muscle_name

    async def wait_for_desired_pressure(self, timeout_ms: int = 10000) -> None:
        """Block the execution until current pressuregen pressure is equal or more than desired pressure."""
        start = time()
        while True:
            await asyncio.sleep(0.01)
            if time() - start >= timeout_ms / 1000:
                raise DesiredPressureNotAchievedError(timeout_ms)

            info = await self.get_pressuregen_info()
            if info.pressure >= info.desired_pressure:
                break

    async def set_muscles(self, muscles: MuscleMovementsDataType) -> None:
        """Send instruction to the controller to set any muscle into certain position"""
        await self.controller_tunnel.set_muscles(muscles)

    async def get_pressures(self) -> Optional[MusclePressuresDataType]:
        """Send request to get the latest muscle pressures."""
        pressures_record = await self.state_tunnel.get_pressures()
        if pressures_record is None:
            return None

        return pressures_record[1]

    async def get_tracking(self) -> Optional[TrackingRecord]:
        """Send request to get the latest muscle pressures."""
        return await self.state_tunnel.get_tracking()

    async def loose_all(self) -> None:
        """Send instruction to the controller to loose all muscles."""
        await self.controller_tunnel.loose_all()

    async def lock_all(self) -> None:
        """Send instruction to the controller to lock all muscles."""
        await self.controller_tunnel.lock_all()

    async def start_pressuregen(self) -> None:
        """Start pressuregen"""
        await self.controller_tunnel.start_pressuregen()

    async def stop_pressuregen(self) -> None:
        """Stop pressuregen"""
        await self.controller_tunnel.stop_pressuregen()

    async def set_pressuregen_pressure(self, pressure: float) -> None:
        """Stop pressuregen and set new desired pressure"""
        await self.controller_tunnel.set_pressuregen_pressure(pressure)

    async def get_valve_nodes(self, rediscover: bool = False) -> Set[ValveAddress]:
        """Send request to get discovered valve nodes."""
        return await self.controller_tunnel.get_nodes(rediscover)

    async def get_pressuregen_info(self) -> PressureGenInfo:
        """Send request to get current information about pressuregen metadata."""
        pressuregen_info: GRPCPressureGenInfo = await self.controller_tunnel.get_pressuregen_info()
        return convert_grpc_instance_to_own_representation(pressuregen_info, PressureGenInfo)

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
