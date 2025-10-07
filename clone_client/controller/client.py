from typing import AsyncGenerator, AsyncIterable, Optional, Sequence

from google.protobuf.empty_pb2 import Empty  # pylint: disable=E0611

from clone_client.controller.config import ControllerClientConfig
from clone_client.error_frames import handle_response
from clone_client.grpc_client import GRPCAsyncClient
from clone_client.proto.controller_pb2 import (
    ControllerRuntimeConfig,
    Pulse,
    SetImpulsesMessage,
    SetPressuresMessage,
    SetPulsesMessage,
    WaterPumpInfo,
    WaterPumpInfoResponse,
    WaterPumpPressure,
)
from clone_client.proto.controller_pb2_grpc import ControllerGRPCStub
from clone_client.proto.data_types_pb2 import ServerResponse
from clone_client.proto.hardware_driver_pb2 import (
    GetNodesMessage,
    HydraControlMessage,
    NodeMap,
    PinchValveCommands,
    PinchValveControl,
    SendHydraControlMessage,
    SendManyHydraControlMessage,
    SendManyPinchValveCommandMessage,
    SendManyPinchValveControlMessage,
    SendPinchValveCommandMessage,
    SendPinchValveControlMessage,
)
from clone_client.utils import grpc_translated, grpc_translated_async


class ControllerClient(GRPCAsyncClient):
    """Client for sending commands and requests to the controller."""

    def __init__(self, socket_address: str, config: ControllerClientConfig) -> None:
        super().__init__("ControllerClient", socket_address)
        self.stub = ControllerGRPCStub(self.channel)
        self.config = config

    @grpc_translated_async()
    async def get_waterpump_info(self) -> WaterPumpInfo:
        """Send request to get the waterpump info."""
        response: WaterPumpInfoResponse = await self.stub.GetWaterPumpInfo(
            Empty(), timeout=self.config.info_gathering_rpc_timeout
        )
        handle_response(response.response)
        return response.info

    @grpc_translated_async()
    async def set_waterpump_pressure(self, pressure: float) -> None:
        """Send request to set the waterpump pressure."""
        await self.stub.SetWaterPumpPressure(
            WaterPumpPressure(pressure=pressure),
            timeout=self.config.critical_rpc_timeout,
        )

    @grpc_translated_async()
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

    @grpc_translated_async()
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

    @grpc_translated_async()
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

    @grpc_translated_async()
    async def send_pinch_valve_control(
        self, node_id: int, control_mode: PinchValveControl.ControlMode.ValueType, value: int
    ) -> None:
        """Send control to selected pinch valve"""
        if control_mode == PinchValveControl.ControlMode.POSITIONS:
            PinchValveControl.PositionsType.Name(PinchValveControl.PositionsType.ValueType(value))
        message = SendPinchValveControlMessage(
            node_id=node_id, control=PinchValveControl(mode=control_mode, value=value)
        )
        response: ServerResponse = await self.stub.SendPinchValveControl(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated_async()
    async def send_many_pinch_valve_control(self, data: dict[int, PinchValveControl]) -> None:
        """Send mass control to all pinch valves"""
        message = SendManyPinchValveControlMessage(data=data)
        response: ServerResponse = await self.stub.SendManyPinchValveControl(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    async def stream_many_pinch_valve_control(
        self, stream: AsyncIterable[dict[int, PinchValveControl]]
    ) -> None:
        """Start streaming control messages to pinchvalves"""

        async def mapped_stream() -> AsyncIterable[SendManyPinchValveControlMessage]:
            async for data in stream:
                yield SendManyPinchValveControlMessage(data=data)

        response: ServerResponse = await self.stub.StreamManyPinchValveControl(mapped_stream(), timeout=None)
        handle_response(response)

    @grpc_translated_async()
    async def send_pinch_valve_command(
        self,
        node_id: int,
        command: PinchValveCommands.ValueType,
    ) -> None:
        """Send an ON/OFF or VBOOST_ON/VBOOST_OFF command to a pinchvalve"""
        message = SendPinchValveCommandMessage(
            node_id=node_id,
            command=command,
        )
        response: ServerResponse = await self.stub.SendPinchValveCommand(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated_async()
    async def send_many_pinch_valve_command(self, commands: dict[int, PinchValveCommands.ValueType]) -> None:
        """Send ON/OFF or VBOOST_ON/VBOOST_OFF commands to selected pinchvalves"""
        message = SendManyPinchValveCommandMessage(commands=commands)
        response: ServerResponse = await self.stub.SendManyPinchValveCommand(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated_async()
    async def send_hydra_control(
        self,
        node_id: int,
        control_msg: HydraControlMessage,
    ) -> None:
        """Send control to selected Hydra valves"""
        message = SendHydraControlMessage(node_id=node_id, control=control_msg)
        response: ServerResponse = await self.stub.SendHydraControl(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated_async()
    async def send_many_hydra_control(self, data: dict[int, HydraControlMessage]) -> None:
        """Send mass control to all Hydra valves"""
        message = SendManyHydraControlMessage(data=data)
        response: ServerResponse = await self.stub.SendManyHydraControl(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    async def stream_many_hydra_control(self, stream: AsyncIterable[dict[int, HydraControlMessage]]) -> None:
        """Start streaming control messages to Hydra valves"""

        async def mapped_stream() -> AsyncIterable[SendManyHydraControlMessage]:
            async for data in stream:
                yield SendManyHydraControlMessage(data=data)

        response: ServerResponse = await self.stub.StreamManyHydraControl(mapped_stream(), timeout=None)
        handle_response(response)

    @grpc_translated_async()
    async def start_waterpump(self) -> None:
        """Send request to start the waterpump."""
        await self.stub.StartWaterPump(Empty(), timeout=self.config.critical_rpc_timeout)

    @grpc_translated_async()
    async def stop_waterpump(self) -> None:
        """Send request to stop the waterpump."""
        await self.stub.StopWaterPump(Empty(), timeout=self.config.critical_rpc_timeout)

    @grpc_translated_async()
    async def loose_all(self) -> None:
        """Send request to loose all muscles."""
        await self.stub.LooseMuscles(Empty(), timeout=self.config.continuous_rpc_timeout)

    @grpc_translated_async()
    async def lock_all(self) -> None:
        """Send request to lock all muscles."""
        await self.stub.LockMuscles(Empty(), timeout=self.config.continuous_rpc_timeout)

    @grpc_translated_async()
    async def get_config(self) -> ControllerRuntimeConfig:
        """Get the configuration of the client."""
        response: ControllerRuntimeConfig = await self.stub.GetConfig(
            Empty(), timeout=self.config.info_gathering_rpc_timeout
        )
        return response

    @grpc_translated()
    async def get_nodes(self) -> NodeMap:
        """Get bus_name -> list[(node_id, product_id)] map of discovered nodes per bus"""
        response: NodeMap = await self.stub.GetNodes(GetNodesMessage())
        return response

    @grpc_translated_async()
    async def ping(self) -> None:
        """Check if server is responding."""
        await self.stub.Ping(Empty(), timeout=self.config.info_gathering_rpc_timeout)
