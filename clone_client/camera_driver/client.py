import logging
from typing import Optional

from google.protobuf.empty_pb2 import Empty

from clone_client.camera_driver.config import CameraDriverClientConfig
from clone_client.grpc_client import GRPCAsyncClient
from clone_client.proto.camera_driver_pb2 import (
    AddSinkRequest,
    GetConfigResponse,
    ListSinksRequest,
    ListSinksResponse,
    ListStreamsResponse,
    RemoveAllSinksRequest,
    RemoveSinkRequest,
    Sink,
)
from clone_client.proto.camera_driver_pb2_grpc import CameraDriverServiceStub
from clone_client.utils import grpc_translated_async

L = logging.getLogger(__name__)


class CameraDriverClient(GRPCAsyncClient):
    def __init__(self, socket_address: str, config: CameraDriverClientConfig) -> None:
        super().__init__("CameraDriver", socket_address)
        self.stub = CameraDriverServiceStub(self.channel)
        self._config = config

    @grpc_translated_async()
    async def get_config(self) -> str:
        resp: GetConfigResponse = await self.stub.GetConfig(Empty())
        return resp.config

    @grpc_translated_async()
    async def list_streams(self) -> list[str]:
        resp: ListStreamsResponse = await self.stub.ListStreams(Empty())
        return list(resp.streams)

    @grpc_translated_async()
    async def list_sinks(self, stream_id: str) -> list[Sink]:
        req = ListSinksRequest(stream_id=stream_id)
        resp: ListSinksResponse = await self.stub.ListSinks(req)
        return list(resp.sinks)

    @grpc_translated_async()
    async def add_sink(
        self,
        stream_id: str,
        address: str,
        port: int,
        multicast_iface: Optional[str] = None,
    ) -> None:
        sink = Sink(
            address=address,
            port=port,
            multicast_iface=multicast_iface or "",
        )
        req = AddSinkRequest(stream_id=stream_id, sink=sink)

        await self.stub.AddSink(
            req,
            timeout=self._config.continuous_rpc_timeout,
        )

    @grpc_translated_async()
    async def remove_sink(
        self,
        stream_id: str,
        address: str,
        port: int,
    ) -> None:
        req = RemoveSinkRequest(
            stream_id=stream_id,
            address=address,
            port=port,
        )
        await self.stub.RemoveSink(
            req,
            timeout=self._config.continuous_rpc_timeout,
        )

    @grpc_translated_async()
    async def remove_all_sinks(self, stream_id: str) -> None:
        req = RemoveAllSinksRequest(stream_id=stream_id)
        await self.stub.RemoveAllSinks(
            req,
            timeout=self._config.continuous_rpc_timeout,
        )
