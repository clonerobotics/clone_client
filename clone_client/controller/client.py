from typing import AsyncGenerator, AsyncIterable, Optional, Sequence

from google.protobuf.empty_pb2 import Empty  # pylint: disable=E0611

from clone_client.controller.config import ControllerClientConfig
from clone_client.controller.proto.controller_pb2 import (
    ControllerRuntimeConfig,
    Pulse,
    SetImpulsesMessage,
    SetPressuresMessage,
    SetPulsesMessage,
    WaterPumpInfo,
    WaterPumpInfoResponse,
    WaterPumpPressure,
)
from clone_client.controller.proto.controller_pb2_grpc import ControllerGRPCStub
from clone_client.error_frames import handle_response
from clone_client.grpc_client import GRPCAsyncClient
from clone_client.proto.data_types_pb2 import ServerResponse
from clone_client.utils import grpc_translated
from clone_client.valve_driver.proto.valve_driver_pb2 import GetNodesMessage, NodeList


class ControllerClient(GRPCAsyncClient):
    """Client for sending commands and requests to the controller."""

    def __init__(self, socket_address: str, config: ControllerClientConfig) -> None:
        super().__init__("ControllerClient", socket_address)
        self.stub = ControllerGRPCStub(self.channel)
        self.config = config

    @grpc_translated()
    async def get_waterpump_info(self) -> WaterPumpInfo:
        """Send request to get the waterpump info."""
        response: WaterPumpInfoResponse = await self.stub.GetWaterPumpInfo(
            Empty(), timeout=self.config.info_gathering_rpc_timeout
        )
        handle_response(response.response)
        return response.info

    @grpc_translated()
    async def set_waterpump_pressure(self, pressure: float) -> None:
        """Send request to set the waterpump pressure."""
        await self.stub.SetWaterPumpPressure(
            WaterPumpPressure(pressure=pressure),
            timeout=self.config.critical_rpc_timeout,
        )

    @grpc_translated()
    async def set_impulses(self, impulses: Sequence[Optional[float]]) -> None:
        """Send request to set the muscles."""
        message = SetImpulsesMessage()
        for move in impulses:
            if move is None:
                message.impulses.add().ignore = True
            else:
                message.impulses.add().value = move

        response: ServerResponse = await self.stub.SetImpulses(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated()
    async def set_pulses(self, pulses: Sequence[Optional[Pulse]]) -> None:
        """Send request to set the muscles."""
        message = SetPulsesMessage()
        for pulse in pulses:
            if pulse is None:
                message.pulses.add().ignore = True
            else:
                message.pulses.append(pulse)
        response: ServerResponse = await self.stub.SetPulses(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated()
    async def set_pressures(self, pressures: Sequence[float]) -> None:
        """Send request to set the pressures."""
        message = SetPressuresMessage(pressures=pressures)
        response: ServerResponse = await self.stub.SetPressures(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    async def stream_set_pressures(self, stream: AsyncIterable[Sequence[float]]) -> None:
        """Start streaming pressures control"""

        async def mapped_stream() -> AsyncGenerator[SetPressuresMessage, None]:
            async for pressures in stream:
                yield SetPressuresMessage(pressures=pressures)

        response: ServerResponse = await self.stub.StreamSetPressures(mapped_stream(), timeout=None)
        handle_response(response)

    @grpc_translated()
    async def start_waterpump(self) -> None:
        """Send request to start the waterpump."""
        await self.stub.StartWaterPump(Empty(), timeout=self.config.critical_rpc_timeout)

    @grpc_translated()
    async def stop_waterpump(self) -> None:
        """Send request to stop the waterpump."""
        await self.stub.StopWaterPump(Empty(), timeout=self.config.critical_rpc_timeout)

    @grpc_translated()
    async def loose_all(self) -> None:
        """Send request to loose all muscles."""
        await self.stub.LooseMuscles(Empty(), timeout=self.config.continuous_rpc_timeout)

    @grpc_translated()
    async def lock_all(self) -> None:
        """Send request to lock all muscles."""
        await self.stub.LockMuscles(Empty(), timeout=self.config.continuous_rpc_timeout)

    @grpc_translated()
    async def get_config(self) -> ControllerRuntimeConfig:
        """Get the configuration of the client."""
        response: ControllerRuntimeConfig = await self.stub.GetConfig(
            Empty(), timeout=self.config.info_gathering_rpc_timeout
        )
        return response

    @grpc_translated()
    async def get_all_nodes(self, rediscover: bool) -> NodeList:
        """Get ids of nodes present on both telemetry and control lines"""
        response: NodeList = await self.stub.GetAllNodes(GetNodesMessage(rediscover=rediscover))
        return response

    @grpc_translated()
    async def get_controlline_nodes(self, rediscover: bool) -> NodeList:
        """Get ids of nodes present on control line"""
        response: NodeList = await self.stub.GetControllineNodes(GetNodesMessage(rediscover=rediscover))
        return response

    @grpc_translated()
    async def get_telemetryline_nodes(self, rediscover: bool) -> NodeList:
        """Get ids of nodes present on telemetry line"""
        response: NodeList = await self.stub.GetTelemetrylineNodes(GetNodesMessage(rediscover=rediscover))
        return response

    @grpc_translated()
    async def ping(self) -> None:
        """Check if server is responding."""
        await self.stub.Ping(Empty(), timeout=self.config.info_gathering_rpc_timeout)
