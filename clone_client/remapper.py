from collections.abc import Sequence
import io
import json
from os import PathLike
from typing import Annotated, Any

from clone_client.types import ValveAddress

MuscleMapping = dict[Annotated[int, "Valve address"], Annotated[str, "Valve name"]]
MuscleOrdering = dict[Annotated[str, "Valve name"], Annotated[int, "Valve position"]]
MuscleOrderingRev = dict[Annotated[int, "Valve position"], Annotated[str, "Valve name"]]
MuscleMappingPathOrFile = str | bytes | PathLike | io.TextIOBase


class Remapper:
    """Class for remapping vectors of data from and to the golem. To reshuffle
    a vector from the golem use .remote_to_local() and .local_to_remote() for reverse.
    """

    def __init__(
        self, remote_ordering: MuscleOrdering, local_ordering: MuscleOrdering | MuscleMappingPathOrFile
    ) -> None:
        if isinstance(local_ordering, MuscleMappingPathOrFile):
            local_ordering = self.ordering_from_json(local_ordering)
        if len(remote_ordering) != len(local_ordering):
            raise ValueError("Remote and target ordering must have same length")
        if not self._check_same_names(remote_ordering, local_ordering):
            raise ValueError("Remote and local ordering must have same muscle names")

        self._remote_to_local = self._indices_map_from_orderings(remote_ordering, local_ordering)
        self._local_to_remote = self._indices_map_from_orderings(local_ordering, remote_ordering)

    def remote_to_local(self, data: Sequence[float]) -> list[float]:
        """Function remaps a sequence from a golem onto their local (current) meaning"""
        return [data[idx] for idx in self._local_to_remote]

    def local_to_remote(self, data: Sequence[float]) -> list[float]:
        """Function remaps a local sequence (created according to current rules)
        onto their remote meaning (how they are interpreted by the golem)
        """
        return [data[idx] for idx in self._remote_to_local]

    @staticmethod
    def swap_ordering(ordering_rev: MuscleOrderingRev) -> MuscleOrdering:
        """Function swaps keys and values of ordering. For use to change reverted
        ordering returned by client (dict[int, str]) to a map from names to indices.
        Note: for this function to work correctly, values of an input dict (muscles' names)
        cannot repeat themselves.
        TODO: this function could be redundant if in client was an accessor
        to ._ordering field.
        """
        return {name: i for i, name in ordering_rev.items()}

    @classmethod
    def ordering_from_json(cls, file: MuscleMappingPathOrFile) -> MuscleOrdering:
        """Function opens a muscle mapping file ('muscles.json') and created a muscle
        mapping dictionary from it
        """
        if isinstance(file, io.TextIOBase):
            mapping_f = json.load(file)
        else:
            with open(file, encoding="utf-8") as f:
                mapping_f = json.load(f)
        mapping = cls._mapping_from_json(mapping_f)
        return cls._create_ordering(mapping)

    @staticmethod
    def _check_same_names(dict1: dict, dict2: dict) -> bool:
        return set(dict1.keys()) == set(dict2.keys())

    @staticmethod
    def _create_ordering(mapping: MuscleMapping) -> MuscleOrdering:
        return {name: i for i, (_, name) in enumerate(sorted(mapping.items()))}

    @staticmethod
    def _indices_map_from_orderings(ordering_in: MuscleOrdering, ordering_out: MuscleOrdering) -> list[int]:
        mapping = {ordering_in[name]: ordering_out[name] for name in ordering_in}
        return [idx_out for _, idx_out in sorted(mapping.items())]

    @staticmethod
    def _mapping_from_json(json_file: Any) -> MuscleMapping:
        return {
            ValveAddress.from_str(field["valve_address"]).pack(): str(field["name"]) for field in json_file
        }
