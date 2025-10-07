from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import cast, Mapping


@dataclass(frozen=True)
class ValveAddress:
    """Represents a valve address."""

    def __str__(self) -> str:
        return f"{self.node_id:02X}:{self.valve_id}"

    def __repr__(self) -> str:
        return f"ValveAddress({self.node_id=:02X}, {self.valve_id=})"

    node_id: int
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

    @classmethod
    def from_str(cls, string: str) -> ValveAddress:
        """Function creates a ValveAddress from a string in format
        '0x[hex control board address]:[dec valve in the control board]'.
        E.g. '0x21:37' -> 0x2100 + 37 = 8485"""
        node_id_s, valve_id_s = string.split(":")
        node_id, valve_id = int(node_id_s, 0), int(valve_id_s, 0)
        assert 0 <= node_id < 256
        assert 0 <= valve_id < 256
        return ValveAddress(node_id, valve_id)


UnpackedValveAddressToMuscleName = Mapping[int, str]
