from datetime import datetime
from typing import AsyncIterable, List, Optional, Tuple

from google.protobuf.empty_pb2 import Empty  # pylint: disable=no-name-in-module
from grpc import RpcError

from clone_client.error_frames import handle_response, translate_rpc_error
from clone_client.grpc_client import GRPCAsyncClient

# pylint: disable=E0611
from clone_client.proto.data_types_pb2 import MusclePressuresState

# pylint: enable=E0611
from clone_client.state_store.config import StateStoreClientConfig

# pylint: disable=E0611
from clone_client.state_store.proto.state_store_pb2 import (
    HandInfo,
    HandInfoResponse,
    PublishedPressures,
    PublishedPressuresList,
)
from clone_client.state_store.proto.state_store_pb2_grpc import StateStorePublisherStub
from clone_client.types import MusclePressuresDataType

ValvePressuresRecord = Tuple[datetime, MusclePressuresDataType]


class StateStoreReceiverClient(GRPCAsyncClient):
    """Client for receiving data from the state store."""

    def __init__(self, socket_address: str, timeout: Optional[float] = None) -> None:
        super().__init__("StateStoreReceiver", socket_address)
        self.stub: StateStorePublisherStub = StateStorePublisherStub(self.channel)
        self._hand_info: Optional[HandInfo] = None

        if timeout is None:
            timeout = StateStoreClientConfig().continuous_rpc_timeout

        self.timeout = timeout

    async def subscribe_pressures(self) -> AsyncIterable[ValvePressuresRecord]:
        """Send request to subscribe to muscle pressures updates."""
        try:
            response: PublishedPressures
            async for response in self.stub.SubscribePressures(Empty(), timeout=self.timeout):
                handle_response(response.response_data)
                yield _unpack_valve_pressure(response.pressures)

        except RpcError as err:
            golem_err = translate_rpc_error("SubscribePressures", self.socket_address, err)
            raise golem_err from err

    async def get_pressures(self) -> ValvePressuresRecord:
        """Send request to get the latest muscle pressures."""
        try:
            response: PublishedPressures = await self.stub.GetPressures(Empty(), timeout=self.timeout)
            handle_response(response.response_data)
            return _unpack_valve_pressure(response.pressures)

        except RpcError as err:
            golem_err = translate_rpc_error("GetPressures", self.socket_address, err)
            raise golem_err from err

    async def get_n_pressure_records(self) -> List[ValvePressuresRecord]:
        """Send request to get the latest n muscle pressures records."""
        try:
            response: PublishedPressuresList = await self.stub.GetLastNPressures(
                Empty(), timeout=self.timeout
            )
            handle_response(response.response_data)
            record: MusclePressuresState
            result: List[ValvePressuresRecord] = []
            for record in response.pressure_list:
                result.append(_unpack_valve_pressure(record))
            return result

        except RpcError as err:
            golem_err = translate_rpc_error("GetLastN_Pressures", self.socket_address, err)
            raise golem_err from err

    async def get_hand_info(self, reload: bool = False) -> HandInfo:
        """Send request to get the hand info."""
        try:
            if reload or not self._hand_info:
                response: HandInfoResponse = await self.stub.GetHandInfo(
                    Empty(), timeout=StateStoreClientConfig().info_gathering_rpc_timeout
                )
                return HandInfo(muscles=response.info.muscles)

            return self._hand_info

        except RpcError as err:
            golem_err = translate_rpc_error("GetHandInfo", self.socket_address, err)
            raise golem_err from err


def configured_subscriber(address: str) -> StateStoreReceiverClient:
    """Create a StateStoreReceiver with the default configuration."""
    timeout = StateStoreClientConfig().continuous_rpc_timeout
    return StateStoreReceiverClient(address, timeout=timeout)


def _unpack_valve_pressure(message: MusclePressuresState) -> ValvePressuresRecord:
    timestamp: datetime = message.timestamp.ToDatetime()
    return timestamp, message.pressures
