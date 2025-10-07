# mypy: disable-error-code="no-any-unimported"
from collections import deque
from itertools import repeat
import json
from pathlib import Path
from typing import Annotated, Mapping, Optional, Self, Sequence

import numpy as np
from scipy import interpolate

from clone_client.proto.state_store_pb2 import Bfield, PoseEstimationInfo, TelemetryData


def rewrap_telemetry(telemetry: TelemetryData) -> dict[int, Sequence[float]]:
    """Convinience function to rewrap data from a telemetry stream so it is prepared
    to be passed to `PoseEstimatorMagInterpol.get_angles_dict`"""
    return {nodeid: bfield.bfield for nodeid, bfield in telemetry.sensor_data.bfields.items()}


class PoseEstimatorMagInterpol:
    """Joint angle estimator using RBF interpolator basing on mapping angle->Bfield
    from a selected file"""

    def __init__(
        self,
        interpolators: dict[int, interpolate.RBFInterpolator],
        filter_avg_samples: int = 8,
        filter_avg_use: bool = False,
        qpos_to_nodeid: Optional[
            dict[int, tuple[Annotated[int, "nodeid"], Annotated[int, "interp idx"]]]
        ] = None,
        qpos_len: Optional[int] = None,
    ) -> None:
        self._filter_avg_use: bool = filter_avg_use
        self._filter_avg_samples: int = filter_avg_samples
        assert self._filter_avg_samples > 0, "Filter samples number must be greater than zero"

        self._interpolators: dict[int, interpolate.RBFInterpolator] = interpolators
        self._filt_samples: dict[int, deque[np.ndarray]] = {}
        for snsr_nr in interpolators:
            if self._filter_avg_use:
                self._filt_samples[snsr_nr] = deque(
                    repeat(np.zeros((4, 3)), self._filter_avg_samples), maxlen=self._filter_avg_samples
                )

        self._qpos_to_nodeid: Optional[
            dict[int, tuple[Annotated[int, "nodeid"], Annotated[int, "interp idx"]]]
        ] = qpos_to_nodeid
        self._qpos_len: Optional[int] = qpos_len

    @classmethod
    def from_interpol_mapping_file(cls, interpol_mapping_path: str) -> Self:
        """Create a magnetic interpolator from a file with angle -> bfield map"""
        mapping = cls._load_interpol_mapping(Path(interpol_mapping_path))
        interpolators = {}
        for snsr_nr, val in mapping.items():
            if val is None:
                continue
            interpolators[snsr_nr] = interpolate.RBFInterpolator(
                np.array([B for _, B in val]),
                [(angle[0], angle[1]) for angle, _ in val],
                kernel="linear",
            )
        return cls(interpolators)

    @classmethod
    def from_maginterp_info(
        cls,
        info: PoseEstimationInfo,
        joint_axis_name2qpos: dict[tuple[str, str], int],
        filter_avg_samples: int = 8,
        filter_avg_use: bool = False,
    ) -> Self:
        """Create a magnetic interpolator from data obtained from state-store"""
        interpolators: dict[int, interpolate.RBFInterpolator] = {}
        qpos_to_nodeid: dict[int, tuple[int, int]] = {}

        for joint_name, joint in info.maginterp.magmap.items():
            angles = np.array([p.angles_rad for p in joint.angle_bfield_points])
            bfields = np.array([p.bfields_teslas for p in joint.angle_bfield_points])
            assert len(angles) == len(bfields)
            interpolator = interpolate.RBFInterpolator(bfields, angles, kernel="linear")
            interpolators[joint.gauss_rider_id] = interpolator

            if joint.HasField("axis0name"):
                qpos_to_nodeid[joint_axis_name2qpos[(joint_name, joint.axis0name)]] = joint.gauss_rider_id, 0
            if joint.HasField("axis1name"):
                qpos_to_nodeid[joint_axis_name2qpos[(joint_name, joint.axis1name)]] = joint.gauss_rider_id, 1

        return cls(interpolators, filter_avg_samples, filter_avg_use, qpos_to_nodeid, info.qpos_len)

    @staticmethod
    def _load_interpol_mapping(
        map_path: Path,
    ) -> dict[int, Optional[list[tuple[tuple[float, float], np.ndarray]]]]:
        """Returns jnt_nr -> (angles, B)"""
        with map_path.open("r") as fp:
            map_ = json.load(fp)
        return {
            int(snsr_nr): (
                [((float(ang[0]), float(ang[1])), np.array(B).ravel()) for ang, B in snsr_map]
                if snsr_map is not None
                else None
            )
            for snsr_nr, snsr_map in map_.items()
        }

    def _filter_avg(self, b_new: dict[int, np.ndarray]) -> dict[int, np.ndarray]:
        # if needed use substract-add algorithm
        # though I'm not sure it'd be more efficient than plain numpy mean
        bs_filtered = {}
        for snsr_nr, bs in self._filt_samples.items():
            try:
                bs.append(b_new[snsr_nr])
            except KeyError:
                bs.append(bs[-1])
            bs_filtered[snsr_nr] = np.mean(np.array(bs), axis=0)
        return bs_filtered

    def get_angles_dict(self, B_tot: Mapping[int, Bfield]) -> dict[int, np.ndarray]:
        """Returns angles in radians for each sensor by its id."""
        # pylint: disable=invalid-name
        angle_dict = {}
        B_arr = {nodeid: np.asarray(B.bfield, dtype=np.double).reshape(4, 3) for nodeid, B in B_tot.items()}
        if self._filter_avg_use:
            B_filtered = self._filter_avg(B_arr)
        else:
            B_filtered = B_arr

        for snsr_nr, B in B_filtered.items():
            interpol = self._interpolators[snsr_nr]
            if interpol is None:
                continue
            angles = interpol(B.ravel()[np.newaxis, :]).ravel()
            angle_dict[snsr_nr] = np.deg2rad(angles)

        return angle_dict

    def get_angles_vec(
        self, B_tot: Mapping[int, Bfield], qpos_vec: Optional[Sequence[float]] = None
    ) -> np.ndarray:
        """Returns angles in radians for each sensor as numpy array of doubles.
        Must be created with `from_maginterp_info()` to use it."""
        # pylint: disable=invalid-name
        if self._qpos_to_nodeid is None:
            raise RuntimeError("Pose estimator info not given")
        if qpos_vec is not None:
            qpos_vec: np.ndarray = np.asarray(qpos_vec)  # type: ignore[no-redef]
        else:
            qpos_vec: np.ndarray = np.zeros(self._qpos_len)  # type: ignore[no-redef]
        angles = self.get_angles_dict(B_tot)
        for qpos, (nodeid, anglesidx) in self._qpos_to_nodeid.items():
            qpos_vec[qpos] = angles[nodeid][anglesidx]
        return qpos_vec  # type: ignore
