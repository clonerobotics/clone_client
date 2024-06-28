from typing import Set

from google.protobuf.empty_pb2 import Empty  # pylint: disable=no-name-in-module
from grpc import RpcError

# pylint: enable=E0611
from clone_client.controller.config import ControllerClientConfig

# pylint: disable=E0611
from clone_client.controller.proto.controller_pb2 import (
    ControllerRuntimeConfig,
    ValveListResponse,
    WaterPumpInfo,
    WaterPumpInfoResponse,
)
from clone_client.controller.proto.controller_pb2_grpc import ControllerGRPCStub
from clone_client.error_frames import handle_response, translate_rpc_error
from clone_client.grpc_client import GRPCAsyncClient

# pylint: disable=E0611
from clone_client.proto.data_types_pb2 import (
    GetNodesRequest,
    MuscleMovement,
    MusclePressureSetting,
    MusclePulse,
    PulseType,
    ServerResponse,
    WaterPumpPressure,
)
from clone_client.types import (
    MuscleMovementsDataType,
    MusclePressuresDataType,
    MusclePulsesDataType,
    ValveAddress,
)

# pylint: enable=E0611


class ControllerClient(GRPCAsyncClient):
    """Client for sending commands and requests to the controller."""

    def __init__(self, socket_address: str, config: ControllerClientConfig) -> None:
        super().__init__("ControllerClient", socket_address)
        self.stub = ControllerGRPCStub(self.channel)
        self.config = config

    async def get_waterpump_info(self) -> WaterPumpInfo:
        """Send request to get the waterpump info."""
        try:
            response: WaterPumpInfoResponse = await self.stub.GetWaterPumpInfo(
                Empty(), timeout=self.config.info_gathering_rpc_timeout
            )
            handle_response(response.response)
            return response.info

        except RpcError as err:
            golem_err = translate_rpc_error("GetWaterPumpInfo", self.socket_address, err)
            raise golem_err from err

    async def set_waterpump_pressure(self, pressure: float) -> None:
        """Send request to set the waterpump pressure."""
        try:
            await self.stub.SetWaterPumpPressure(
                WaterPumpPressure(pressure=pressure),
                timeout=self.config.critical_rpc_timeout,
            )

        except RpcError as err:
            golem_err = translate_rpc_error("SetWaterPumpPressure", self.socket_address, err)
            raise golem_err from err

    async def set_muscles(self, movements: MuscleMovementsDataType) -> None:
        """Send request to set the muscles."""
        try:
            # Map to protobuf schema
            request = MuscleMovement()
            for move in movements:
                if move is None:
                    request.movements.add().ignore = True
                else:
                    request.movements.add().value = move

            response: ServerResponse = await self.stub.SetMuscles(
                request, timeout=self.config.continuous_rpc_timeout
            )
            handle_response(response)

        except RpcError as err:
            golem_err = translate_rpc_error("SetMuscles", self.socket_address, err)
            raise golem_err from err

    async def set_pulses(self, pulses: MusclePulsesDataType) -> None:
        """Send request to set the muscles."""
        try:
            # Map to protobuf schema
            request = MusclePulse()
            for pulse in pulses:
                if pulse is None:
                    request.pulses.add().ignore = True
                else:
                    entry = request.pulses.add()
                    entry.value.ctrl_type = PulseType.IN if pulse[0] == 0 else PulseType.OUT
                    entry.value.pulse_len_ms = pulse[1]
                    entry.value.delay_len_ms = pulse[2]
                    entry.value.duration_ms = pulse[3]
            response: ServerResponse = await self.stub.SetPulses(
                request, timeout=self.config.continuous_rpc_timeout
            )
            handle_response(response)

        except RpcError as err:
            golem_err = translate_rpc_error("SetPulses", self.socket_address, err)
            raise golem_err from err

    async def set_pressures(self, pressures: MusclePressuresDataType) -> None:
        """Send request to set the pressures."""
        try:
            request = MusclePressureSetting(pressures=pressures)
            response: ServerResponse = await self.stub.SetPressures(
                request, timeout=self.config.continuous_rpc_timeout
            )
            handle_response(response)

        except RpcError as err:
            golem_err = translate_rpc_error("SetPressures", self.socket_address, err)
            raise golem_err from err

    async def start_waterpump(self) -> None:
        """Send request to start the waterpump."""
        try:
            await self.stub.StartWaterPump(Empty(), timeout=self.config.critical_rpc_timeout)
        except RpcError as err:
            golem_err = translate_rpc_error("StartWaterPump", self.socket_address, err)
            raise golem_err from err

    async def stop_waterpump(self) -> None:
        """Send request to stop the waterpump."""
        try:
            await self.stub.StopWaterPump(Empty(), timeout=self.config.critical_rpc_timeout)
        except RpcError as err:
            golem_err = translate_rpc_error("StopWaterPump", self.socket_address, err)
            raise golem_err from err

    async def loose_all(self) -> None:
        """Send request to loose all muscles."""
        try:
            await self.stub.LooseMuscles(Empty(), timeout=self.config.continuous_rpc_timeout)
        except RpcError as err:
            golem_err = translate_rpc_error("LooseMuscles", self.socket_address, err)
            raise golem_err from err

    async def lock_all(self) -> None:
        """Send request to lock all muscles."""
        try:
            await self.stub.LockMuscles(Empty(), timeout=self.config.continuous_rpc_timeout)
        except RpcError as err:
            golem_err = translate_rpc_error("LockMuscles", self.socket_address, err)
            raise golem_err from err

    async def get_nodes(self, rediscover: bool = False) -> Set[ValveAddress]:
        """Send request to get discovered nodes."""
        try:
            request = GetNodesRequest(rediscover=rediscover)
            response: ValveListResponse = await self.stub.GetValves(
                request, timeout=self.config.info_gathering_rpc_timeout
            )

            handle_response(response.response)

            return {ValveAddress.unpack(addr) for addr in response.valve_list.values.keys()}

        except RpcError as err:
            golem_err = translate_rpc_error("GetNodes", self.socket_address, err)
            raise golem_err from err

    async def get_config(self) -> ControllerRuntimeConfig:
        """Get the configuration of the client."""
        try:
            response: ControllerRuntimeConfig = await self.stub.GetConfig(
                Empty(), timeout=self.config.info_gathering_rpc_timeout
            )
            return response
        except RpcError as err:
            golem_err = translate_rpc_error("GetConfig", self.socket_address, err)
            raise golem_err from err


def configured_controller_client(address: str) -> ControllerClient:
    """Create a ControllerClient with the default configuration."""
    config = ControllerClientConfig()

    return ControllerClient(address, config)
