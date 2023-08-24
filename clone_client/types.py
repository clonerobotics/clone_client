from __future__ import annotations

import dataclasses
import struct
from typing import cast, Mapping, Sequence

Pressure = float
Angle = int

PortAddress = str
ValveID = str
NodeID = int
MuscleName = str

ValveAnglesDataType = Mapping[NodeID, Angle]
ValveMusclePressuresDataType = Mapping[NodeID, Pressure]
ValveMuscleMovementsDataType = Mapping[NodeID, float]
MusclePressuresDataType = Sequence[Pressure]  # For client side translations only
MuscleMovementsDataType = Sequence[float]  # For client side translations only
ValveAddressPacked = int


@dataclasses.dataclass(frozen=True)
class ValveAddress:
    """Represents a valve address."""

    def __str__(self) -> str:
        return f"{self.node_id:02X}:{self.valve_id}"

    def __repr__(self) -> str:
        return f"ValveAddress({self.node_id=:02X}, {self.valve_id=})"

    node_id: NodeID
    valve_id: int

    def pack(self) -> int:
        """Packs a valve address into an integer."""
        buf = struct.pack("=BB", self.valve_id, self.node_id)
        return cast(int, struct.unpack("=H", buf)[0])

    @classmethod
    def unpack(cls, packed: int) -> ValveAddress:
        """Unpacks a packed valve address into a ValveAddress object."""
        valve_id, node_id = struct.unpack("=BB", struct.pack("=H", packed))

        return ValveAddress(node_id, valve_id)


UnpackedValveAddressToMuscleName = Mapping[int, MuscleName]


@dataclasses.dataclass
class HandInfo:
    """Information about the hand."""

    muscles: UnpackedValveAddressToMuscleName


@dataclasses.dataclass
class CompressorInfo:
    """Information about the compressor."""

    desired_pressure: float
    pressure: float
    is_running: bool
