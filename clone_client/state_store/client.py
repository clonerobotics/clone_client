from typing import AsyncIterable, Optional, Sequence

from google.protobuf.empty_pb2 import Empty  # pylint: disable=E0611

from clone_client.error_frames import handle_response
from clone_client.grpc_client import GRPCAsyncClient
from clone_client.proto.state_store_pb2 import (
    SystemInfo,
    SystemInfoResponse,
    TelemetryData,
    TelemetryDataResponse,
)
from clone_client.proto.state_store_pb2_grpc import StateStoreReceiverGRPCStub
from clone_client.state_store.config import StateStoreClientConfig
from clone_client.utils import grpc_translated_async


class StateStoreReceiverClient(GRPCAsyncClient):
    """Client for receiving data from the state store."""

    def __init__(self, socket_address: str, config: StateStoreClientConfig) -> None:
        super().__init__("StateStoreReceiver", socket_address)
        self.stub: StateStoreReceiverGRPCStub = StateStoreReceiverGRPCStub(self.channel)
        self._system_info: Optional[SystemInfo] = None
        self._config = config

    async def subscribe_telemetry(self) -> AsyncIterable[TelemetryData]:
        """Send request to subscribe to muscle pressures updates."""
        response: TelemetryDataResponse
        # timeout must be none to allow the client to wait indefinitely,
        # otherwise it crashes after said timeout
        async for response in self.stub.SubscribeTelemetry(Empty(), timeout=None):
            handle_response(response.response_data)
            yield response.data

    @grpc_translated_async()
    async def get_telemetry(self) -> TelemetryData:
        """Send request to get the latest muscle pressures."""
        response: TelemetryDataResponse = await self.stub.GetTelemetry(
            Empty(), timeout=self._config.continuous_rpc_timeout
        )
        handle_response(response.response_data)

        return response.data

    @grpc_translated_async()
    async def get_system_info(self, reload: bool = False) -> SystemInfo:
        """Send request to get the hand info."""
        if reload or not self._system_info:
            response: SystemInfoResponse = await self.stub.GetSystemInfo(
                Empty(), timeout=self._config.info_gathering_rpc_timeout
            )
            self._system_info = response.info

        return self._system_info

    @grpc_translated_async()
    async def ping(self) -> None:
        """Check if server is responding."""
        await self.stub.Ping(Empty(), timeout=self._config.info_gathering_rpc_timeout)
