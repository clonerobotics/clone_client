import asyncio
import logging
from typing import Any, Sequence, Tuple, TypedDict

import grpc
import grpc.aio

from clone_client.config import CONFIG
from clone_client.utils import retry, url_rfc_to_grpc

LOGGER = logging.getLogger(__name__)


class ChannelArgs(TypedDict):
    """Type for gRPC channel arguments."""

    target: str
    options: Sequence[Tuple[str, Any]]


class GRPCAsyncClient:
    """Base class for gRPC async clients."""

    def __init__(self, name: str, socket_address: str) -> None:
        self._name = name
        self._socket_address = socket_address
        self._channel_args = self._setup_channel_args()
        self._channel = grpc.aio.insecure_channel(**self._channel_args)

        LOGGER.info("[gRPC:%s] Connecting to %s", self._name, self._socket_address)

    @property
    def channel(self) -> grpc.aio.Channel:  # type: ignore
        """Return gRPC channel."""
        return self._channel

    @property
    def socket_address(self) -> str:
        """Return socket address."""
        return self._socket_address

    def _setup_channel_args(self) -> ChannelArgs:
        """Setup channel arguments."""
        return {
            "target": url_rfc_to_grpc(self._socket_address),
            "options": [("grpc.keepalive_timeout_ms", 500)],
        }

    @retry(max_retries=CONFIG.max_retries, catch=[asyncio.TimeoutError])
    async def channel_ready(self, timeout_s: int = 2) -> bool:  # pylint: disable=invalid-overridden-method
        """Wait for channel to be ready."""
        LOGGER.info(
            "[gRPC:%s] Waiting for channel at %s to be ready...", self._name, self._channel_args["target"]
        )
        return await asyncio.wait_for(self.channel.channel_ready(), timeout_s)
