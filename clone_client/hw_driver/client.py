import logging
from typing import Annotated

from google.protobuf.empty_pb2 import Empty

from clone_client.error_frames import get_request_error
from clone_client.grpc_client import GRPCAsyncClient
from clone_client.hw_driver.config import HWDriverClientConfig
from clone_client.proto.hardware_driver_pb2 import (
    GaussRiderSpecSettings,
    GaussRiderSpecSettingsResponse,
    GetNodesMessage,
    NodeMap,
)
from clone_client.proto.hardware_driver_pb2_grpc import HardwareDriverGRPCStub
from clone_client.utils import grpc_translated

L = logging.getLogger(__name__)


class HWDriverClient(GRPCAsyncClient):
    """Client for receiving data from the state store."""

    def __init__(self, socket_address: str, config: HWDriverClientConfig) -> None:
        super().__init__("HardwareDriver", socket_address)
        self.stub = HardwareDriverGRPCStub(self.channel)
        self._config = config

    @grpc_translated()
    async def get_nodes(self) -> NodeMap:
        """Get bus_name -> list[(node_id, product_id)] map of discovered nodes per bus"""
        response: NodeMap = await self.stub.GetNodes(GetNodesMessage())
        return response

    @grpc_translated()
    async def get_gauss_rider_spec_settings(self) -> dict[Annotated[int, "node id"], GaussRiderSpecSettings]:
        """Get specific settings of GaussRiders present in a runnning system - they consist of
        calibration data"""
        response: GaussRiderSpecSettingsResponse = await self.stub.GetGaussRiderSpecSettings(
            Empty(), timeout=self._config.continuous_rpc_timeout
        )
        match response.WhichOneof("inner"):
            case "success":
                return dict(response.success.spec_settings)
            case "error":
                raise get_request_error(response.error)
            case None:
                raise ValueError("Got None instead of any expected value")
