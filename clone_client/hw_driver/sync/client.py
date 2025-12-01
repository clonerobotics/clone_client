from dataclasses import dataclass
from enum import IntEnum
import logging
from typing import Annotated, Optional, Self

from google.protobuf.empty_pb2 import Empty
import grpc

from clone_client.error_frames import get_request_error, handle_response
from clone_client.grpc_client import GRPCClient
from clone_client.hw_driver.config import HWDriverClientConfig
from clone_client.proto.data_types_pb2 import ErrorInfo, ServerResponse
from clone_client.proto.hardware_driver_pb2 import (
    DiscoveryMessage,
    DiscoveryResponse,
    GaussRiderSpecSettings,
    GaussRiderSpecSettingsResponse,
    GetNodesMessage,
    GetNodesSettingsMessage,
    GetNodesSettingsResponse,
    HwDriverErrors,
)
from clone_client.proto.hardware_driver_pb2 import (
    NodeGenericSettings as ProtoNodeGenericSettings,
)
from clone_client.proto.hardware_driver_pb2 import BusDevice as ProtoBusDevice
from clone_client.proto.hardware_driver_pb2 import NodeMap, PingNodeMessage
from clone_client.proto.hardware_driver_pb2_grpc import HardwareDriverGRPCStub
from clone_client.utils import grpc_translated

L = logging.getLogger(__name__)


class ProductId(IntEnum):
    """Product IDs of used snail-proto devices"""

    # pylint: disable=invalid-name
    ServoValve = 0x00
    ServoValveStepper = 0x01
    Spider = 0x02
    Watch = 0x03
    Kolektiv = 0x04
    Uroboros = 0x05
    KolektivV5 = 0x06
    Imu = 0x07
    Heater = 0x08
    KolektivV3Ctrl = 0x09
    KolektivV3Data = 0x0A
    KolektivV3CtrlMonitoring = 0x0B
    KolektivV3DataMonitoring = 0x0C
    MagneticHub = 0x0D
    PinchValve = 0x0E
    GaussRider = 0x0F
    Hydra1 = 0x10
    Hydra6 = 0x11
    Hydra8 = 0x12
    Hydra10 = 0x13
    UNKNOWN = 0xFF


class PingNodeBusResponse(IntEnum):
    """Does a node answered the ping?"""

    RESERVED = 0
    FOUND = 1
    NOT_FOUND = 2
    BUS_ERROR = 3


@dataclass
class NodeGenericSettings:
    """Generic (common) settings of snail-proto devices"""

    node_id: int
    product_id: ProductId
    pcb_id: int
    device_random_id: int
    _valve_hold_duty: int
    _pad3: int = 0

    @classmethod
    def from_proto(cls, proto: ProtoNodeGenericSettings) -> Self:
        """Create `NodeGenericSettings` from protobuf transport class"""
        return cls(
            node_id=proto.node_id,
            product_id=ProductId(proto.product_id),
            pcb_id=proto.pcb_id,
            device_random_id=proto.device_random_id,
            _valve_hold_duty=proto._valve_hold_duty,  # pylint: disable=protected-access
            _pad3=proto._pad3,  # pylint: disable=protected-access
        )


@dataclass
class BusDevice:
    """Class describing a bus device."""

    node_id: int
    product_id: ProductId

    @classmethod
    def from_proto(cls, proto: ProtoBusDevice) -> Self:
        """Create `BusDevice` from protobuf transport class"""
        return cls(node_id=proto.node_id, product_id=ProductId(proto.product_id))


@dataclass
class HardwareDriverErrors:
    """Empty list: lack of recent errors;
    None: errors buffering disabled"""

    hw_driver_errors: Optional[list[ErrorInfo]]
    buses_errors: dict[str, Optional[list[ErrorInfo]]]


class HWDriverClient(GRPCClient[grpc.Channel]):
    """Client for receiving data from the state store."""

    def __init__(self, socket_address: str, config: HWDriverClientConfig) -> None:
        super().__init__("HardwareDriver", socket_address)
        self.stub = HardwareDriverGRPCStub(self.channel)
        self._config = config

    @classmethod
    def new(cls, socket_address: str) -> "HWDriverClient":
        """Create and initialize new `HWDriverClient` instance"""
        self = cls(socket_address, HWDriverClientConfig())
        self.channel_ready()
        return self

    @grpc_translated()
    def get_nodes(self) -> dict[str, list[BusDevice]]:
        """Get bus_name -> list[(node_id, product_id)] map of discovered nodes per bus"""
        response: NodeMap = self.stub.GetNodes(
            GetNodesMessage(), timeout=self._config.continuous_rpc_timeout
        )
        ret = {bus: list(map(BusDevice.from_proto, nodes.nodes)) for bus, nodes in response.nodes.items()}
        return ret

    @grpc_translated()
    def get_gauss_rider_spec_settings(self) -> dict[Annotated[int, "node id"], GaussRiderSpecSettings]:
        """Get specific settings of GaussRiders present in a runnning system - they consist of
        calibration data"""
        response: GaussRiderSpecSettingsResponse = self.stub.GetGaussRiderSpecSettings(
            Empty(), timeout=self._config.continuous_rpc_timeout
        )
        match response.WhichOneof("inner"):
            case "success":
                return dict(response.success.spec_settings)
            case "error":
                raise get_request_error(response.error)
            case None:
                raise ValueError("Got None instead of any expected value")

    @grpc_translated()
    def ping_node(self, node_id: int, bus_name: str, timeout_us: int = 1000) -> None:
        """Ping selected node. This will trigger pinging on all buses governed
        by a hardware-driver. If error or not found - raise.
        NOTE: GRPC timeout is set to 2.0 * timeout_us to receive golem ServerResponse with timeout
        instead of GRPC one."""
        response: ServerResponse = self.stub.PingNode(
            PingNodeMessage(node_id=node_id, bus_name=bus_name, timeout_us=timeout_us),
            timeout=(timeout_us * 2.0) / 1000_000,
        )
        handle_response(response)

    @grpc_translated()
    def discovery(
        self,
        bus_name: str,
        discovery_ranges: list[tuple[int, int]] = [(0, 253)],
        discovery_blacklist: list[int] = [],
        timeout_us: int = 5_000_000,
    ) -> list[Annotated[int, "node id"]]:
        """Conduct discovery on a selected bus.
        Setting ids in `discovery_blacklist` will cause not-pinging those nodes
        even if they are in selected ranges.
        This function causes no side-effects on golem, i.e. if discovered device
        list will differ from one discovered on golem's startup, it will neither
        supersede it nor cause any error.
        NOTE: To short timeout set will cause not all (or none) of pinged nodes
        will answer in the timeout and will be considered as not present.
        NOTE: GRPC timeout is set to 2.0 * timeout_us to receive golem ServerResponse with timeout
        instead of GRPC one."""
        # pylint: disable=dangerous-default-value
        response: DiscoveryResponse = self.stub.Discovery(
            DiscoveryMessage(
                bus_name=bus_name,
                timeout_us=timeout_us,
                discovery_ranges=map(
                    lambda r: DiscoveryMessage.DiscoveryRange(start_node=r[0], end_node=r[1]),
                    discovery_ranges,
                ),
                discovery_blacklist=discovery_blacklist,
            ),
            timeout=(timeout_us * 2.0) / 1000_000,
        )
        handle_response(response.server_response)
        return list(response.node_ids)

    @grpc_translated()
    def get_nodes_settings(
        self, bus_name: str, node_ids: list[int], timeout_us: int = 1000_000
    ) -> dict[int, Optional[NodeGenericSettings]]:
        """Get generic settings of selected devices.
        Returns map node_id -> Optional[settings] where None means an error during reception process.
        NOTE: GRPC timeout is set to 2.0 * timeout_us to receive golem ServerResponse with timeout
        instead of GRPC one."""
        response: GetNodesSettingsResponse = self.stub.GetNodesSettings(
            GetNodesSettingsMessage(bus_name=bus_name, node_ids=node_ids, timeout_us=timeout_us),
            timeout=(timeout_us * 2.0) / 1000_000,
        )
        return {
            node_id: (
                NodeGenericSettings.from_proto(node_settings.settings) if node_settings is not None else None
            )
            for node_id, node_settings in response.settings.items()
        }

    @grpc_translated()
    def get_errors(
        self,
    ) -> HardwareDriverErrors:
        """Get hardware drivers errors"""
        response: HwDriverErrors = self.stub.GetErrors(
            Empty(), timeout=self._config.continuous_rpc_timeout
        )
        if response.HasField("hw_driver_errors"):
            hw_driver_errors = list(response.hw_driver_errors.errors)
        else:
            L.warning("Errors buffering disabled for the hardware-driver")
            hw_driver_errors = None
        buses_errors: dict[str, Optional[list[ErrorInfo]]] = {}
        for bus_name, bus_errors in response.buses_errors.items():
            if bus_errors.HasField("errors_list"):
                buses_errors[bus_name] = list(bus_errors.errors_list.errors)
            else:
                L.warning("Errors buffering disabled for bus: %s", bus_name)
                buses_errors[bus_name] = None

        return HardwareDriverErrors(hw_driver_errors=hw_driver_errors, buses_errors=buses_errors)
