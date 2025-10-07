from typing import Generator, Iterable, Optional, Sequence

from google.protobuf.empty_pb2 import Empty  # pylint: disable=E0611
import grpc

from clone_client.controller.config import ControllerClientConfig
from clone_client.error_frames import handle_response
from clone_client.grpc_client import GRPCClient
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
from clone_client.utils import grpc_translated


class ControllerClient(GRPCClient[grpc.Channel]):
    """Client for sending commands and requests to the controller."""

    def __init__(self, socket_address: str, config: ControllerClientConfig) -> None:
        super().__init__("ControllerClient", socket_address)
        self.stub = ControllerGRPCStub(self.channel)
        self.config = config

    @grpc_translated()
    def get_waterpump_info(self) -> WaterPumpInfo:
        """Send request to get the waterpump info."""
        response: WaterPumpInfoResponse = self.stub.GetWaterPumpInfo(
            Empty(), timeout=self.config.info_gathering_rpc_timeout
        )
        handle_response(response.response)
        return response.info

    @grpc_translated()
    def set_waterpump_pressure(self, pressure: float) -> None:
        """Send request to set the waterpump pressure."""
        self.stub.SetWaterPumpPressure(
            WaterPumpPressure(pressure=pressure),
            timeout=self.config.critical_rpc_timeout,
        )

    @grpc_translated()
    def set_impulses(self, impulses: Sequence[Optional[float]]) -> None:
        """Send request to set the muscles."""
        message = SetImpulsesMessage()
        for move in impulses:
            if move is None:
                message.impulses.add().ignore = True
            else:
                message.impulses.add().value = move

        response: ServerResponse = self.stub.SetImpulses(message, timeout=self.config.continuous_rpc_timeout)
        handle_response(response)

    @grpc_translated()
    def set_pulses(self, pulses: Sequence[Optional[Pulse]]) -> None:
        """Send request to set the muscles."""
        message = SetPulsesMessage()
        for pulse in pulses:
            if pulse is None:
                message.pulses.add().ignore = True
            else:
                message.pulses.append(pulse)
        response: ServerResponse = self.stub.SetPulses(message, timeout=self.config.continuous_rpc_timeout)
        handle_response(response)

    @grpc_translated()
    def set_pressures(self, pressures: Sequence[float]) -> None:
        """Send request to set the pressures."""
        message = SetPressuresMessage(pressures=pressures)
        response: ServerResponse = self.stub.SetPressures(message, timeout=self.config.continuous_rpc_timeout)
        handle_response(response)

    def stream_set_pressures(self, stream: Iterable[Sequence[float]]) -> None:
        """Start streaming pressures control"""

        def mapped_stream() -> Generator[SetPressuresMessage, None, None]:
            for pressures in stream:
                yield SetPressuresMessage(pressures=pressures)

        response: ServerResponse = self.stub.StreamSetPressures(mapped_stream(), timeout=None)
        handle_response(response)

    @grpc_translated()
    def send_pinch_valve_control(
        self, node_id: int, control_mode: PinchValveControl.ControlMode.ValueType, value: int
    ) -> None:
        """Send control to selected pinch valve"""
        if control_mode == PinchValveControl.ControlMode.POSITIONS:
            PinchValveControl.PositionsType.Name(PinchValveControl.PositionsType.ValueType(value))
        message = SendPinchValveControlMessage(
            node_id=node_id, control=PinchValveControl(mode=control_mode, value=value)
        )
        response: ServerResponse = self.stub.SendPinchValveControl(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated()
    def send_many_pinch_valve_control(self, data: dict[int, PinchValveControl]) -> None:
        """Send mass control to all pinch valves"""
        message = SendManyPinchValveControlMessage(data=data)
        response: ServerResponse = self.stub.SendManyPinchValveControl(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    def stream_many_pinch_valve_control(self, stream: Iterable[dict[int, PinchValveControl]]) -> None:
        """Start streaming control messages to pinchvalves"""

        def mapped_stream() -> Iterable[SendManyPinchValveControlMessage]:
            for data in stream:
                yield SendManyPinchValveControlMessage(data=data)

        response: ServerResponse = self.stub.StreamManyPinchValveControl(mapped_stream(), timeout=None)
        handle_response(response)

    @grpc_translated()
    def send_pinch_valve_command(
        self,
        node_id: int,
        command: PinchValveCommands.ValueType,
    ) -> None:
        """Send an ON/OFF or VBOOST_ON/VBOOST_OFF command to a pinchvalve"""
        message = SendPinchValveCommandMessage(
            node_id=node_id,
            command=command,
        )
        response: ServerResponse = self.stub.SendPinchValveCommand(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated()
    def send_many_pinch_valve_command(self, commands: dict[int, PinchValveCommands.ValueType]) -> None:
        """Send ON/OFF or VBOOST_ON/VBOOST_OFF commands to selected pinchvalves"""
        message = SendManyPinchValveCommandMessage(commands=commands)
        response: ServerResponse = self.stub.SendManyPinchValveCommand(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated()
    def send_hydra_control(
        self,
        node_id: int,
        control_msg: HydraControlMessage,
    ) -> None:
        """Send control to selected Hydra valves"""
        message = SendHydraControlMessage(node_id=node_id, control=control_msg)
        response: ServerResponse = self.stub.SendHydraControl(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    @grpc_translated()
    def send_many_hydra_control(self, data: dict[int, HydraControlMessage]) -> None:
        """Send mass control to all Hydra valves"""
        message = SendManyHydraControlMessage(data=data)
        response: ServerResponse = self.stub.SendManyHydraControl(
            message, timeout=self.config.continuous_rpc_timeout
        )
        handle_response(response)

    def stream_many_hydra_control(self, stream: Iterable[dict[int, HydraControlMessage]]) -> None:
        """Start streaming control messages to Hydra valves"""

        def mapped_stream() -> Iterable[SendManyHydraControlMessage]:
            for data in stream:
                yield SendManyHydraControlMessage(data=data)

        response: ServerResponse = self.stub.StreamManyHydraControl(mapped_stream(), timeout=None)
        handle_response(response)

    @grpc_translated()
    def start_waterpump(self) -> None:
        """Send request to start the waterpump."""
        self.stub.StartWaterPump(Empty(), timeout=self.config.critical_rpc_timeout)

    @grpc_translated()
    def stop_waterpump(self) -> None:
        """Send request to stop the waterpump."""
        self.stub.StopWaterPump(Empty(), timeout=self.config.critical_rpc_timeout)

    @grpc_translated()
    def loose_all(self) -> None:
        """Send request to loose all muscles."""
        self.stub.LooseMuscles(Empty(), timeout=self.config.continuous_rpc_timeout)

    @grpc_translated()
    def lock_all(self) -> None:
        """Send request to lock all muscles."""
        self.stub.LockMuscles(Empty(), timeout=self.config.continuous_rpc_timeout)

    @grpc_translated()
    def get_config(self) -> ControllerRuntimeConfig:
        """Get the configuration of the client."""
        response: ControllerRuntimeConfig = self.stub.GetConfig(
            Empty(), timeout=self.config.info_gathering_rpc_timeout
        )
        return response

    @grpc_translated()
    def get_nodes(self) -> NodeMap:
        """Get bus_name -> list[(node_id, product_id)] map of discovered nodes per bus"""
        response: NodeMap = self.stub.GetNodes(GetNodesMessage())
        return response

    @grpc_translated()
    def ping(self) -> None:
        """Check if server is responding."""
        self.stub.Ping(Empty(), timeout=self.config.info_gathering_rpc_timeout)
