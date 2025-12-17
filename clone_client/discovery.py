import asyncio
import logging
import socket
from typing import List, Optional, Tuple

from zeroconf import IPVersion, Zeroconf
from zeroconf.asyncio import (
    AsyncServiceBrowser,
    AsyncServiceInfo,
    AsyncZeroconf,
    ServiceListener,
)

from clone_client.config import CommunicationService, CONFIG
from clone_client.exceptions import ClientError
from clone_client.utils import strip_local

LOGGER = logging.getLogger(__name__)


class AsyncThreadSafeEvent(asyncio.Event):
    """Thread safe event for asyncio."""

    def set(self) -> None:
        self._loop.call_soon_threadsafe(super().set)  # type: ignore


class ServiceNotFoundError(ClientError):
    """Raised when service cannot be found on the server.""" ""

    def __init__(self, server: str, service: str) -> None:
        message = f"Service {service} cannot be find on the {server}."
        super().__init__(message)


class Discovery(ServiceListener):
    """Base class for discovering services on the network."""

    TYPE = "_golem._tcp.local."

    def __init__(
        self,
        server: str,
        service: CommunicationService,
        verify: bool = True,
        timeout_s: float = 3,
    ) -> None:
        self._server = strip_local(server)
        self.service = service
        self._timeout_s = timeout_s
        self._address: Optional[Tuple[str, int]] = None
        self._verify = verify

        self._found_address_timeout = AsyncThreadSafeEvent()

    def discover_sync(self) -> Tuple[str, int]:
        return asyncio.get_event_loop().run_until_complete(self.discover())

    async def discover(self) -> Tuple[str, int]:
        """
        Discover specified service.
        Raise `ServiceNotFoundError` if discovery time exceeded configured timeout.
        """
        LOGGER.info("Discovering %s on %s", self.service.name, self._server)

        zeroconf = AsyncZeroconf()
        browser = AsyncServiceBrowser(zeroconf=zeroconf.zeroconf, type_=self.TYPE, listener=self)
        # ServiceBrowser runs a sweeping loop inside a thread
        # In order to wait for any result for a specified period of time
        # we have to wait for event to occurr
        try:
            await asyncio.wait_for(self._found_address_timeout.wait(), self._timeout_s)
            if not self._address:
                raise ServiceNotFoundError(self._server, self.service.name)

            return self._address
        except asyncio.TimeoutError as terr:
            raise ServiceNotFoundError(self._server, self.service.name) from terr
        finally:
            await browser.async_cancel()
            await zeroconf.async_close()

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Add a device that became visible via zeroconf."""
        asyncio.ensure_future(self.async_add_service(zc, type_, name))

    async def _verify_address(self, valid_addresses: List[str], port: int) -> Optional[Tuple[str, int]]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(10)

        try:
            LOGGER.info("Verifying addresses availability %s", valid_addresses)
            while True:  # This seems like an infinite loop but discover method takes care of timeout
                for address in valid_addresses:
                    LOGGER.debug("Trying to connect to %s using %r", self.service.name, address)
                    result = sock.connect_ex((address, port))
                    sock.close()

                    if result == 0:
                        LOGGER.info("Found connection for %s. Using %s.", self.service.name, address)
                        return (address, port)

                    await asyncio.sleep(0.1)
        finally:
            sock.close()

    async def async_add_service(self, zconf: Zeroconf, type_: str, name: str) -> None:
        """ServiceListener specific function"""
        if self._address:
            return

        info = AsyncServiceInfo(type_, name)
        await info.async_request(zconf, self._timeout_s)

        if not info or not info.server:
            return

        info_server = strip_local(info.server)
        if self._server != info_server:
            # Check for suffixed version of the server
            try:
                raw, _suffix = info_server.rsplit("-", 1)
            except ValueError:
                return

            if self._server != raw:
                return

            LOGGER.info("Found suffixed server %s. for %s.", info_server, self._server)

        if self.service.name not in name:
            return

        valid_addresses = info.parsed_addresses(version=IPVersion.V4Only)
        port = info.port
        if port is None or not valid_addresses:
            return

        if self._verify:
            self._address = await self._verify_address(valid_addresses, port)
        else:
            address = valid_addresses[0]
            LOGGER.info("Skipping connection verify. Using available address: %s.", address)
            self._address = (address, port)

        self._found_address_timeout.set()

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """ServiceListener specific function"""

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """ServiceListener specific function"""
