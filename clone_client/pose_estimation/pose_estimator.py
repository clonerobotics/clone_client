# mypy: disable-error-code="no-any-unimported"
from collections import deque
from dataclasses import dataclass
from itertools import repeat
from typing import Annotated, Literal, Mapping

import numpy as np
import numpy.typing as npt
from scipy import interpolate
from scipy.spatial.transform import Rotation as R

from clone_client.proto.state_store_pb2 import Bfield, PoseEstimationInfo, TelemetryData


@dataclass
class MagInterpolConfig:
    """Additional parameters for client"""

    filter_avg_use: bool = True
    filter_avg_samples: int = 8


def axis_to_index(axis: str | Literal["X", "Y", "Z"] | None) -> Literal[0, 1, 2] | None:
    """Convert a standard axis name ("X", "Y", "Z", also in lowercase) to a corresponding index
    number (0, 1, 2). When axis does not match the said names, raises `RuntimeError`"""
    if axis is None:
        return None
    axis = axis.upper()
    if axis == "X":
        return 0
    if axis == "Y":
        return 1
    if axis == "Z":
        return 2
    raise RuntimeError(f"Wrong axis name '{axis}'")


class PoseEstimatorMagInterpol:
    """Joint angle estimator using RBF interpolator basing on mapping angle->Bfield
    from a selected file"""

    class RBFInterpolatorProxy(interpolate.RBFInterpolator):
        # pylint: disable=invalid-name
        """RBFInterpolator as in SciPy, though extended with calculation of SciPy's Rotations,
        basing on given indices telling how to interpret returned angles, i.e. whether
        the first and second angles returned from the interpolator should be interpreted
        as the Rotation's X, Y or Z axis (XYZ intrinsic euler)."""

        def __init__(  # type: ignore[no-untyped-def]
            self,
            y: npt.NDArray[np.double],
            d: npt.NDArray[np.double],
            axes: tuple[str | Literal["X", "Y", "Z"] | None, str | Literal["X", "Y", "Z"] | None],
            **kwargs,
        ) -> None:
            super().__init__(y, d, **kwargs)
            self._indices = [axis_to_index(axes[0]), axis_to_index(axes[1])]
            self._angles = [0.0] * 3

        def __call__(self, B: npt.NDArray[np.double]) -> R:
            angles_interp = super().__call__(B.ravel()[np.newaxis, :]).ravel()
            idx0 = self._indices[0]
            if idx0 is not None:
                self._angles[idx0] = angles_interp[0]
            idx1 = self._indices[1]
            if idx1 is not None:
                self._angles[idx1] = angles_interp[1]
            return R.from_euler("XYZ", self._angles, degrees=True)

    def __init__(
        self,
        interpolators: dict[Annotated[str, "joint name"], RBFInterpolatorProxy],
        nodeid_to_jnt_name: dict[int, str],
        filter_avg_samples: int = 8,
        filter_avg_use: bool = False,
    ) -> None:
        self._node_to_jnt_name: dict[int, str] = nodeid_to_jnt_name

        self._interpolators: dict[
            Annotated[str, "joint name"], PoseEstimatorMagInterpol.RBFInterpolatorProxy
        ] = interpolators

        self._filter_avg_use: bool = filter_avg_use
        self._filter_avg_samples: int = filter_avg_samples
        assert self._filter_avg_samples > 0, "Filter samples number must be greater than zero"
        self._filt_samples: deque[npt.NDArray[np.double]]
        self._filt_joint_name_sequence: list[Annotated[str, "joint name"]]
        self._filt_curr_state: npt.NDArray[np.double]
        if self._filter_avg_use:
            self._filt_samples = deque(
                repeat(np.zeros((len(nodeid_to_jnt_name), 4, 3)), self._filter_avg_samples),
                maxlen=self._filter_avg_samples,
            )
            self._filt_curr_state = np.zeros((len(nodeid_to_jnt_name), 4, 3))
            self._filt_joint_name_sequence = list(self._interpolators.keys())

    @classmethod
    def from_maginterp_info(
        cls,
        info: PoseEstimationInfo,
        filter_avg_samples: int = 8,
        filter_avg_use: bool = False,
    ) -> "PoseEstimatorMagInterpol":
        """Create a magnetic interpolator from data obtained from state-store"""
        interpolators: dict[str, cls.RBFInterpolatorProxy] = {}
        nodeid_to_jnt_name: dict[int, str] = {}

        for joint_name, joint in info.maginterp.magmap.items():
            angles = np.array([p.angles_rad for p in joint.angle_bfield_points])
            bfields = np.array([p.bfields_teslas for p in joint.angle_bfield_points])
            assert len(angles) == len(bfields)
            interpolator_ext = cls.RBFInterpolatorProxy(
                bfields,
                angles,
                axes=(
                    joint.axis0name if joint.HasField("axis0name") else None,
                    joint.axis1name if joint.HasField("axis1name") else None,
                ),
                kernel="linear",
            )
            interpolators[joint_name] = interpolator_ext
            nodeid_to_jnt_name[joint.gauss_rider_id] = joint_name

        return cls(
            interpolators,
            nodeid_to_jnt_name,
            filter_avg_samples,
            filter_avg_use,
        )

    def _filter_avg(self, b_new: dict[Annotated[str, "joint_name"], np.ndarray]) -> dict[str, np.ndarray]:
        # if needed use substract-add algorithm
        # though I'm not sure it'd be more efficient than plain numpy mean
        bs = (
            np.array(
                [
                    b_new[joint_name] if joint_name in b_new else self._filt_samples[idx][-1]
                    for idx, joint_name in enumerate(self._filt_joint_name_sequence)
                ]
            )
            / self._filter_avg_samples
        )
        self._filt_curr_state -= self._filt_samples[0]
        self._filt_samples.append(bs)
        self._filt_curr_state += bs
        return {
            joint_name: self._filt_curr_state[idx]
            for idx, joint_name in enumerate(self._filt_joint_name_sequence)
        }

    def get_rotations_dict(self, B_tot: Mapping[int, Bfield]) -> dict[Annotated[str, "joint name"], R]:
        """Returns angles in radians for each sensor by its id."""
        # pylint: disable=invalid-name
        angle_dict = {}
        B_arr = {
            self._node_to_jnt_name[node_id]: np.asarray(B.bfield, dtype=np.double).reshape(4, 3)
            for node_id, B in B_tot.items()
            if node_id in self._node_to_jnt_name
        }
        if self._filter_avg_use:
            B_filtered = self._filter_avg(B_arr)
        else:
            B_filtered = B_arr

        for joint_name, B in B_filtered.items():
            interpol = self._interpolators.get(joint_name, None)
            if interpol is None:
                continue
            angle_dict[joint_name] = interpol(B.ravel()[np.newaxis, :])

        return angle_dict
