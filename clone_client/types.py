from __future__ import annotations

import dataclasses
import struct
from typing import cast, Mapping, Sequence

Pressure = float
NodeID = int
MuscleName = str

MusclePressuresDataType = Sequence[Pressure]  # For client side translations only
MuscleMovementsDataType = Sequence[float]  # For client side translations only


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
class PressureGenInfo:
    """Information about the pressuregen."""

    desired_pressure: float
    pressure: float
    is_running: bool
    temperature: float
    is_active: bool
    variant: str
