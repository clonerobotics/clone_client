from typing import Set

from google.protobuf.empty_pb2 import Empty  # pylint: disable=no-name-in-module
from grpc import RpcError

# pylint: enable=E0611
from clone_client.controller.config import ControllerClientConfig

# pylint: disable=E0611
from clone_client.controller.proto.supervisor_pb2 import (
    CompressorInfo,
    CompressorInfoResponse,
    ValveListResponse,
)
from clone_client.controller.proto.supervisor_pb2_grpc import SupervisorGRPCStub
from clone_client.error_frames import handle_response, translate_rpc_error
from clone_client.grpc_client import GRPCAsyncClient

# pylint: disable=E0611
from clone_client.proto.data_types_pb2 import (
    CompressorPressure,
    GetNodesRequest,
    MuscleMovement,
    MusclePressureSetting,
    ServerResponse,
)
from clone_client.types import (
    MuscleMovementsDataType,
    MusclePressuresDataType,
    ValveAddress,
)

# pylint: enable=E0611


class ControllerClient(GRPCAsyncClient):
    """Client for sending commands and requests to the controller."""

    def __init__(self, socket_address: str, config: ControllerClientConfig) -> None:
        super().__init__("ControllerClient", socket_address)
        self.stub = SupervisorGRPCStub(self.channel)
        self.config = config

    async def get_compressor_info(self) -> CompressorInfo:
        """Send request to get the compressor info."""
        try:
            response: CompressorInfoResponse = await self.stub.GetCompressorInfo(
                Empty(), timeout=self.config.info_gathering_rpc_timeout
            )
            handle_response(response.response)
            return response.info

        except RpcError as err:
            golem_err = translate_rpc_error("GetCompressorInfo", self.socket_address, err)
            raise golem_err from err

    async def set_compressor_pressure(self, pressure: float) -> None:
        """Send request to set the compressor pressure."""
        try:
            await self.stub.SetCompressorPressure(
                CompressorPressure(pressure=pressure),
                timeout=self.config.critical_rpc_timeout,
            )

        except RpcError as err:
            golem_err = translate_rpc_error("SetCompressorPressure", self.socket_address, err)
            raise golem_err from err

    async def set_muscles(self, movements: MuscleMovementsDataType) -> None:
        """Send request to set the muscles."""
        try:
            request = MuscleMovement(movements=movements)
            response: ServerResponse = await self.stub.SetMuscles(
                request, timeout=self.config.continuous_rpc_timeout
            )
            handle_response(response)

        except RpcError as err:
            golem_err = translate_rpc_error("SetMuscles", self.socket_address, err)
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

    async def start_compressor(self) -> None:
        """Send request to start the compressor."""
        try:
            await self.stub.StartCompressor(Empty(), timeout=self.config.critical_rpc_timeout)
        except RpcError as err:
            golem_err = translate_rpc_error("StartCompressor", self.socket_address, err)
            raise golem_err from err

    async def stop_compressor(self) -> None:
        """Send request to stop the compressor."""
        try:
            await self.stub.StopCompressor(Empty(), timeout=self.config.critical_rpc_timeout)
        except RpcError as err:
            golem_err = translate_rpc_error("StopCompressor", self.socket_address, err)
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


def configured_controller_client(address: str) -> ControllerClient:
    """Create a ControllerClient with the default configuration."""
    config = ControllerClientConfig()

    return ControllerClient(address, config)
