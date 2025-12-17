import asyncio
import logging
from typing import Any, Generic, Sequence, Tuple, TypedDict, TypeVar

import grpc
import grpc.aio

from clone_client.utils import url_rfc_to_grpc

LOGGER = logging.getLogger(__name__)

T = TypeVar("T", bound=grpc.Channel)  # type: ignore


class ChannelArgs(TypedDict):
    """Type for gRPC channel arguments."""

    target: str
    options: Sequence[Tuple[str, Any]]


class GRPCClient(Generic[T]):
    """Base class for gRPC clients."""

    def __init__(self, name: str, socket_address: str) -> None:
        self._name = name
        self._socket_address = socket_address
        self._channel_args = self._setup_channel_args()
        self._channel: T = grpc.insecure_channel(**self._channel_args)

        LOGGER.info("[gRPC:%s] Connecting to %s", self._name, self._socket_address)

    @property
    def channel(self) -> T:  # type: ignore
        """Return gRPC channel."""
        return self._channel

    @property
    def socket_address(self) -> str:
        """Return socket address"""
        return self._socket_address

    def _setup_channel_args(self) -> ChannelArgs:
        """Setup channel arguments."""
        return {
            "target": url_rfc_to_grpc(self._socket_address),
            # add default_authority not to be rejected because of "malformed authority"
            "options": [("grpc.keepalive_timeout_ms", 500), ("grpc.default_authority", "localhost")],
        }

    def channel_ready(self, timeout_s: int = 6) -> None:
        """Wait for channel to be ready."""
        LOGGER.info(
            "[gRPC:%s] Waiting for channel at %s to be ready...", self._name, self._channel_args["target"]
        )
        return grpc.channel_ready_future(self.channel).result(timeout=timeout_s)


class GRPCAsyncClient(GRPCClient[grpc.aio.Channel]):
    """Base class for gRPC async clients."""

    def __init__(self, name: str, socket_address: str) -> None:
        super().__init__(name, socket_address)
        self._channel = grpc.aio.insecure_channel(**self._channel_args)

    async def channel_ready(self, timeout_s: int = 6) -> None:  # pylint: disable=invalid-overridden-method
        """Wait for channel to be ready."""
        LOGGER.info(
            "[gRPC:%s] Waiting for channel at %s to be ready...", self._name, self._channel_args["target"]
        )
        return await asyncio.wait_for(self.channel.channel_ready(), timeout_s)
