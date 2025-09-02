"""Module containing tools to convert bare measurements from Gauss Riders 
(which use FH3D04 sensors) to B-field values, given in milli Teslas.

To use it thoroughly firstly `CalibrationDataRaw` should be fetched (and possibly cached)
from each used device (they are per sensor). This can currently be done via `HardwareClient`.

In case it cannot be done, `CALIBRATION_OLD_COMPATIBILITY` structure may be used,
which effectively by-passes calibration.

This module is mainly for development purpouses and shortly it will be transfered into the Golem server.
"""

from dataclasses import asdict, dataclass
import json
import logging
from typing import (
    Annotated,
    Callable,
    Literal,
    no_type_check,
    Sequence,
    TypeAlias,
    TypeVar,
)

import numpy as np
from numpy import typing as npt

from clone_client.proto.hardware_driver_pb2 import GaussRiderSpecSettings
from clone_client.proto.state_store_pb2 import GaussRiderRaw

Numeric = TypeVar("Numeric", bound=np.number)
Vec13: TypeAlias = np.ndarray[tuple[Literal[13]], np.dtype[Numeric]]
Vec12: TypeAlias = np.ndarray[tuple[Literal[12]], np.dtype[Numeric]]
Vec4: TypeAlias = np.ndarray[tuple[Literal[4]], np.dtype[Numeric]]
Matrix4x3: TypeAlias = np.ndarray[tuple[Literal[4], Literal[3]], np.dtype[Numeric]]
Matrix4x2: TypeAlias = np.ndarray[tuple[Literal[4], Literal[2]], np.dtype[Numeric]]

L = logging.getLogger(__name__)


def value_chain(*args):  # type: ignore
    """Shamelessly stolen from `more-itertools` module"""
    for value in args:
        if isinstance(value, (str, bytes)):
            yield value
            continue
        try:
            yield from value
        except TypeError:
            yield value


def gauss_rider_rewrap(data: GaussRiderRaw) -> Vec13[np.int16]:
    """Rewrap a data point received from GaussRider telemetry into a numpy array"""
    ret = value_chain([getattr(px, ax) for px in data.sensor.pixels for ax in "xyz"], data.sensor.temperature)
    return np.array(list(ret), dtype=np.int16)  # type: ignore


def gauss_rider_rewrap_many(data: Sequence[GaussRiderRaw]) -> npt.NDArray[Vec13[np.int16]]:
    """Rewrap data series received from GaussRider telemetry into a numpy array"""
    ret = [
        list(value_chain([getattr(px, ax) for px in gr.sensor.pixels for ax in "xyz"], gr.sensor.temperature))
        for gr in data
    ]
    return np.array(ret, dtype=np.int16)  # type: ignore


class FH3D04:
    """Constants related to calibration of FH3D04 sensors"""

    BASIC_GAIN_XY = 128
    BASIC_GAIN_Z = 64
    BASIC_DEC_LEN = 512
    BASIC_SUPPLY = 2.6
    TEMP_DIGIT2CELS = 0.072484471  # deg C / digit


@dataclass
class CalibrationDataRaw:  # pylint: disable=invalid-name
    """Raw calibration data received from a GaussRider in form of arrays"""

    offsets_0: Matrix4x3[np.int16]
    Hval_P_T0: Matrix4x3[np.int16]
    Hval_N_T0: Matrix4x3[np.int16]
    temperatures: Matrix4x3[np.int16]
    Hval_P_T1: Matrix4x3[np.int16]
    Hval_N_T1: Matrix4x3[np.int16]
    offsets_1: Matrix4x3[np.int16]
    Hval_O_P: Matrix4x3[np.int16]
    Hval_O_N: Matrix4x3[np.int16]

    def save(self, filename: str) -> None:
        """Save to a json file"""
        with open(filename, "w") as fp:
            L.debug("Saving file")

            def default(o):  # type: ignore
                if isinstance(o, np.ndarray):
                    return o.tolist()
                if isinstance(o, Sequence):
                    return list(o)
                print(type(o))
                raise TypeError(f"Unknown object: {o}")

            json.dump(asdict(self), fp, indent=4, default=default)
            L.debug("Saved")

    @classmethod
    @no_type_check
    def load(cls, filename: str) -> "CalibrationDataRaw":
        """Load from a json file"""
        with open(filename, "r") as fp:
            L.debug("Loading file")
            input_raw = json.load(fp)
            L.debug("Loaded dict: %s", input_raw)
            ret = cls(
                offsets_0=np.asarray(input_raw["offsets_0"], dtype=np.int16),
                Hval_P_T0=np.asarray(input_raw["Hval_P_T0"], dtype=np.int16),
                Hval_N_T0=np.asarray(input_raw["Hval_N_T0"], dtype=np.int16),
                temperatures=np.asarray(input_raw["temperatures"], dtype=np.int16),
                Hval_P_T1=np.asarray(input_raw["Hval_P_T1"], dtype=np.int16),
                Hval_N_T1=np.asarray(input_raw["Hval_N_T1"], dtype=np.int16),
                offsets_1=np.asarray(input_raw["offsets_1"], dtype=np.int16),
                Hval_O_P=np.asarray(input_raw["Hval_O_P"], dtype=np.int16),
                Hval_O_N=np.asarray(input_raw["Hval_O_N"], dtype=np.int16),
            )
            L.debug("Converted dict: %s", ret)
            return ret

    @classmethod
    @no_type_check
    def from_gauss_spec_settings(cls, settings: GaussRiderSpecSettings) -> "CalibrationDataRaw":
        """Convert specific setings fetched from a GaussRider into a CalibrationDataRaw"""
        return cls(
            offsets_0=np.array(
                settings.offsets_0,
                dtype=np.int16,
            ).reshape((4, 3)),
            Hval_P_T0=np.array(
                settings.Hval_P_T0,
                dtype=np.int16,
            ).reshape((4, 3)),
            Hval_N_T0=np.array(
                settings.Hval_N_T0,
                dtype=np.int16,
            ).reshape((4, 3)),
            temperatures=np.array(
                settings.temperatures,
                dtype=np.int16,
            ).reshape((4, 3)),
            Hval_P_T1=np.array(
                settings.Hval_P_T1,
                dtype=np.int16,
            ).reshape((4, 3)),
            Hval_N_T1=np.array(
                settings.Hval_N_T1,
                dtype=np.int16,
            ).reshape((4, 3)),
            offsets_1=np.array(
                settings.offsets_1,
                dtype=np.int16,
            ).reshape((4, 3)),
            Hval_O_P=np.array(
                settings.Hval_O_P,
                dtype=np.int16,
            ).reshape((4, 3)),
            Hval_O_N=np.array(
                settings.Hval_O_N,
                dtype=np.int16,
            ).reshape((4, 3)),
        )


@dataclass
class Calibration:
    """Structure containing closures calculating dynamic calibration values"""

    # sensitivities S(t_val_pp) = s_t0 + s_scale_coef * t_val_pp
    sensitivity: Callable[[npt.NDArray[np.number]], npt.NDArray[Matrix4x3]]  # mT/digit
    # offsets O(t_val_pp) = o_t0 + o_scale_coef * t_val_pp:
    offsets: Callable[[npt.NDArray[np.number]], npt.NDArray[Matrix4x3]]  # mT
    # orthogonality
    orthogonality: Callable[[npt.NDArray[Vec4[np.number]]], npt.NDArray[Matrix4x2]]  # mT


def _sensitivity_default(_):  # type: ignore
    ret = np.empty((4, 3))
    ret[:, :2] = 0.010687 / 8
    ret[:, 2] = 0.011187 / 16
    return ret


def _offsets_default(_):  # type: ignore
    return np.zeros((4, 3))


def _orthogonality_default(_):  # type: ignore
    return np.zeros((4, 2))


CALIBRATION_OLD_COMPATIBILITY = Calibration(
    sensitivity=_sensitivity_default,
    offsets=_offsets_default,
    orthogonality=_orthogonality_default,
)


class GaussCalculator:
    """Structure for derivation of calibration and calculating B-field values of data from Gauss Riders"""

    @dataclass
    class Config:
        """Configuration of a given sensor"""

        icoil: float = 1.0  # mA

    def __init__(self, calibration: CalibrationDataRaw | Calibration, config: Config = Config()) -> None:
        self._config = config
        if isinstance(calibration, CalibrationDataRaw):
            self._calibration = self._calibration_from_raw(calibration)
        else:
            self._calibration = calibration

    def _calibration_from_raw(self, calibration: CalibrationDataRaw) -> Calibration:
        temperatures = calibration.temperatures.ravel()
        t_val_start = temperatures[0]  # pylint: disable=unused-variable
        t_val_0_tlo = temperatures[2]
        t_val_1_tlo = temperatures[1]
        t_val_0 = temperatures[3]
        t_val_1 = temperatures[4]

        bcoil_xy = 191.0 * self._config.icoil  # uT
        bcoil_z = 182.0 * self._config.icoil  # uT
        signs = np.array(
            [
                [1, 1, 1],
                [1, -1, -1],
                [-1, -1, 1],
                [1, 1, 1],
            ]
        )
        bcoil = np.array([bcoil_xy, bcoil_xy, bcoil_z]) * signs

        # [3] / [4, 3] -> [4, 3]
        s_t_0 = bcoil / ((calibration.Hval_P_T0 - calibration.Hval_N_T0) / 2.0) / 1000_000.0
        s_t_1 = bcoil / ((calibration.Hval_P_T1 - calibration.Hval_N_T1) / 2.0) / 1000_000.0
        s_t_coef = (s_t_1 - s_t_0) / (t_val_1 - t_val_0)
        # [4, 3] + [4, 3] * [x, 1, 1] -> [x, 4, 3]
        s = lambda t_val: s_t_0 + s_t_coef * (t_val[:, np.newaxis, np.newaxis] - t_val_0)

        o_t_0 = calibration.offsets_0.astype(np.double)
        o_t_1 = calibration.offsets_1.astype(np.double)
        o_scale_coef = (o_t_1 - o_t_0) / (t_val_1_tlo - t_val_0_tlo)
        # [4, 3] + [4, 3] * [x, 1, 1] -> [x, 4, 3]
        o = lambda t_val: o_t_0 + o_scale_coef * (t_val[:, np.newaxis, np.newaxis] - t_val_0_tlo)

        h_val_pp_p = calibration.Hval_O_P
        h_val_pp_n = calibration.Hval_O_N
        h_val_pp_diff = h_val_pp_p - h_val_pp_n
        # [4, 2] / [4, 1]
        orth_coef = h_val_pp_diff[:, :2] / h_val_pp_diff[:, 2, np.newaxis]
        # [x, 4, 1] * [1, 4, 2] -> [x, 4, 2] (only XY, hence 2)
        orth = lambda h_val_pp_z: h_val_pp_z[..., np.newaxis] * orth_coef

        ret = Calibration(
            sensitivity=s,
            offsets=o,
            orthogonality=orth,
        )
        return ret

    def calculate_bfield(self, data: Sequence[Vec13[np.int16]]) -> npt.NDArray[Matrix4x3[np.double]]:
        """data: array of raw B and temperature data from a sensor (flattened 4x3 magnetic
        values and 1 temperature value)"""
        # input shape: [x, 13]
        data_arr = np.asarray(data, dtype=np.double)
        # [x]
        t_val = data_arr[:, -1]
        L.debug("T: %s", t_val)
        # [x] -> [x, 4, 3]
        s = self._calibration.sensitivity(t_val)
        L.debug("S: %s", s)
        # [x] -> [x, 4, 3]
        o = self._calibration.offsets(t_val)
        L.debug("O: %s", o)
        # ([x, 4, 3] - [4, 3]) * [4, 3] -> [x, 4, 3]
        B = (data_arr[..., :-1].reshape((-1, 4, 3)) - o) * s  # pylint: disable=invalid-name
        L.debug("B noorth: %s", B)
        # [x, 4] -> [x, 4, 2]
        orth = self._calibration.orthogonality(B[:, :, 2])
        L.debug("Orth: %s", orth)
        # [x, 4, 2] - [x, 4, 2] -> [x, 4, 2]
        B[..., :2] -= orth
        L.debug("B: %s", B)
        # [x, 4, 3]
        return B  # type: ignore
