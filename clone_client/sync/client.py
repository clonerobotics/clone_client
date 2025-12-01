from __future__ import annotations

from dataclasses import dataclass
from enum import auto, Flag
import ipaddress as ip
import logging
from pathlib import Path
from types import TracebackType
from typing import Type

from clone_client.config import CommunicationService, CONFIG
from clone_client.controller.sync.client import ControllerClient
from clone_client.exceptions import ClientError
from clone_client.hw_driver.sync.client import HWDriverClient
from clone_client.pose_estimation.pose_estimator import MagInterpolConfig
from clone_client.state_store.sync.client import StateStoreClient

LOGGER = logging.getLogger(__name__)


class Client:
    # pylint: disable=too-many-public-methods, too-many-instance-attributes
    """Client for sending commands and requests to the controller and state."""

    class TunnelsUsed(Flag):
        """Flag for selecting channels which are going to be used"""

        CONTROLLER = auto()
        STATE = auto()
        HW_DRIVER = auto()

    @dataclass
    class Config:
        """Additional parameters for client"""

        maginterp_config: MagInterpolConfig = MagInterpolConfig()

    def __init__(
        self,
        address: str,
        tunnels_used: TunnelsUsed = TunnelsUsed.CONTROLLER | TunnelsUsed.STATE,
        additional_config: Config = Config(),
    ) -> None:
        self.address = address
        self.tunnels_used = tunnels_used
        self._config = additional_config

        self._controller: ControllerClient
        self._state_store: StateStoreClient
        self._hw_driver: HWDriverClient

    @property
    def controller(self) -> ControllerClient:
        """Get controller"""
        return self._controller

    @property
    def state_store(self) -> StateStoreClient:
        """Get state-store"""
        return self._state_store

    @property
    def hw_driver(self) -> HWDriverClient:
        """Get hardware-driver"""
        return self._hw_driver

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

    def __enter__(self) -> Client:
        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            self._controller = ControllerClient.new(
                self._create_socket_str(CONFIG.communication.controller_service)
            )
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            self._state_store = StateStoreClient.new(
                self._create_socket_str(CONFIG.communication.state_store_service),
                self._config.maginterp_config,
            )
        if Client.TunnelsUsed.HW_DRIVER in self.tunnels_used:
            self._hw_driver = HWDriverClient.new(
                self._create_socket_str(CONFIG.communication.hw_driver_service)
            )

        if Client.TunnelsUsed.STATE in self.tunnels_used:
            self.state_store.get_system_info(reload=True)

        LOGGER.info("Client initialized and ready to use.")

        return self

    def __exit__(self, exc_type: Type[ClientError], value: ClientError, traceback: TracebackType) -> None:
        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            self.controller.channel.__exit__(exc_type, value, traceback)
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            self.state_store.channel.__exit__(exc_type, value, traceback)
        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            self.hw_driver.channel.__exit__(exc_type, value, traceback)

    def ping(self) -> None:
        """Check if server is responding"""
        if Client.TunnelsUsed.STATE in self.tunnels_used:
            self.state_store.ping()
        if Client.TunnelsUsed.CONTROLLER in self.tunnels_used:
            self.controller.ping()
