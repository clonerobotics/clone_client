"""
Get the calibration values (min and max) of the pressure sensors.
Uses current (or default) calibration data to calibrate it again based on the
returned pressure values.

Run it each time you want to calibrate the pressure sensors, i.e. pressure changed.
This should be implemented as a API call in the future for more automation.
"""

import asyncio
import enum
import os
import socket
from typing import AsyncGenerator

import click
from click.termui import itertools
import numpy

from clone_client.client import Client
from clone_client.hw_driver.client import ProductId
from clone_client.proto.hardware_driver_pb2 import (
    HydraControlMessage,
    PinchValveControl,
)

GOLEM_HOSTNAME = os.getenv("GOLEM_HOSTNAME", socket.gethostname())
GOLEM_ADDRESS = os.getenv("GOLEM_ADDRESS", None)
USE_PINCH_VALVES = os.getenv("USE_PINCH_VALVES", False)
ACT_TIME = 5

MUSCLE_WHITELIST = {}


def denormalize_value(normalized_value: float, original_min: int = 0, original_max: int = 8500) -> int:
    """
    Denormalizes a value that was normalized between 0 and 1 back to its original range,
    allowing for values slightly below 0 and above 1 due to sensor inaccuracies.

    :param normalized_value: The normalized value (can be slightly < 0 or > 1)
    :param original_min: The minimum value of the original range (default is 0)
    :param original_max: The maximum value of the original range (default is 8500)
    :return: The denormalized value
    """
    # Calculate the original range
    original_range = original_max - original_min

    # Denormalize the value
    denormalized_value = original_min + (normalized_value * original_range)

    return int(denormalized_value)


async def send_hydra_single(
    client: Client, node_id: int, channel_id: int, message: HydraControlMessage.PositionsType.ValueType
) -> None:
    positions = [HydraControlMessage.OUTLET_FULLY_OPENED] * 10
    positions[channel_id] = message

    await client.controller.send_hydra_control(
        node_id, HydraControlMessage(positions=HydraControlMessage.Positions(positions=positions))
    )


async def send_pinch_valve_single(client: Client, node_id: int, value: int) -> None:
    if value > 0:
        pvalue = PinchValveControl.INLET_FULLY_OPENED
    elif value < 0:
        pvalue = PinchValveControl.OUTLET_FULLY_OPENED
    else:
        pvalue = PinchValveControl.BOTH_CLOSED

    await client.controller.send_pinch_valve_control(
        node_id, control_mode=PinchValveControl.POSITIONS, value=pvalue
    )


async def get_measurements(client: Client, samples: int) -> numpy.ndarray:
    for _ in range(3):
        buf = numpy.zeros((samples, client.state_store.number_of_muscles))
        s = 0

        while 1:
            pvec = (await client.state_store.get_telemetry()).sensor_data.pressures
            if not pvec:
                continue

            buf[s] = numpy.asarray(pvec)
            if s == samples - 1:
                break

            s += 1

        all_valid = not numpy.isnan(buf).any()
        if not all_valid:

            continue
        return buf

    raise ValueError("Encountered NaN values in some muscle readouts")


class CalibrationStep(enum.Enum):
    STARTING = 0
    CALIBRATING_MIN = 1
    CALIBRATING_MAX = 2
    GENERATING = 3
    DONE = 4


async def run_calibration(
    c: Client,
    soft_limit_mb: int,
    setpoint_mb: int,
    threshold_mb: int,
    samples: int,
) -> AsyncGenerator[tuple[CalibrationStep, float | None, str | None], str]:
    calibration_data = {}

    await c.controller.loose_all()
    controller_config = await c.controller.get_config()
    info = await c.state_store.get_system_info()
    nodes = await c.controller.get_nodes()
    all_nodes = {n.node_id: n for n in itertools.chain.from_iterable(nodes.values())}

    for i in range(2):
        yield (CalibrationStep.STARTING, (i + 1) / 2, "Starting measurements...")
        await c.controller.loose_all()
        await asyncio.sleep(3)

    yield (CalibrationStep.CALIBRATING_MIN, None, "Measuring mins...")
    meas_min = numpy.min(await get_measurements(c, samples=samples), axis=0)
    assert meas_min.shape == (c.state_store.number_of_muscles,)

    yield (CalibrationStep.CALIBRATING_MAX, 0.0, None)
    for idx, (mname, minfo) in enumerate(info.muscles.items()):
        vkey = (hex(minfo.node_id), minfo.node_id, minfo.channel_id, mname)
        progress = (idx + 1) / c.state_store.number_of_muscles

        curr_calib_min = info.calibration_data.pressure_sensors[minfo.index].min
        curr_calib_max = info.calibration_data.pressure_sensors[minfo.index].max

        calib_min = 0
        calib_max = 0
        try:
            calib_min = denormalize_value(
                meas_min[minfo.index], original_min=curr_calib_min, original_max=curr_calib_max
            )

            calib_max = calib_min
            node_device = all_nodes[minfo.node_id]
            pid = ProductId(node_device.product_id)

            yield (CalibrationStep.CALIBRATING_MAX, progress, f"Inflating muscle at {vkey}")

            tp_mb = 0
            period_s = 0.1
            stale_count = 10
            await c.controller.lock_all()
            while tp_mb < (setpoint_mb - threshold_mb):
                match pid:
                    case ProductId.Hydra1 | ProductId.Hydra6 | ProductId.Hydra8 | ProductId.Hydra10:
                        await send_hydra_single(
                            c, minfo.node_id, minfo.channel_id, HydraControlMessage.INLET_FULLY_OPENED
                        )
                    case ProductId.PinchValve:
                        await send_pinch_valve_single(c, minfo.node_id, 1)
                    case ProductId.KolektivV3Ctrl:
                        impulses: list[float | None] = [None] * c.state_store.number_of_muscles
                        impulses[minfo.index] = 500 / controller_config.max_impulse_duration_ms
                        await c.controller.set_impulses(impulses)

                await asyncio.sleep(period_s)
                tp = (await c.state_store.get_telemetry()).sensor_data.pressures
                if not tp:
                    continue

                new_tp_mb = denormalize_value(
                    tp[minfo.index], original_min=curr_calib_min, original_max=curr_calib_max
                )

                if new_tp_mb <= (tp_mb + threshold_mb) or (new_tp_mb < 0 and tp_mb < 0):
                    # Does not seem to be increasing, decreasing stale counter
                    stale_count -= 1

                tp_mb = new_tp_mb
                if stale_count == 0:
                    # Muscle is staling, either leaking quite heavily indicating non-connected valve
                    # or pressure sensor is broken / not-connected, or setpoint is mich higher than the source pressure
                    # Either way, measurement seems useless
                    break

            await c.controller.lock_all()
            yield (CalibrationStep.CALIBRATING_MAX, progress, f"Measuring muscle at {vkey}")
            if stale_count == 0 and tp_mb < threshold_mb + soft_limit_mb:
                yield (
                    CalibrationStep.CALIBRATING_MAX,
                    progress,
                    f"Muscle at {vkey} skipped (stale), resetting...",
                )
            else:
                # Muscle is activated properly within measurement threshold, we can start measurements
                meas_max = numpy.max(await get_measurements(c, samples=samples), axis=0)
                calib_max = denormalize_value(
                    meas_max[minfo.index], original_min=curr_calib_min, original_max=curr_calib_max
                )
            yield (CalibrationStep.CALIBRATING_MAX, progress, f"Muscle at {vkey} measured, deflating...")
        except ValueError:
            calib_min = curr_calib_min
            calib_max = curr_calib_max
            yield (
                CalibrationStep.CALIBRATING_MAX,
                progress,
                f"Incorrect base for: {vkey}(min: {curr_calib_min}, {curr_calib_max})",
            )
            continue

        for _ in range(5):
            await c.controller.loose_all()
            await asyncio.sleep(0.1)

        if minfo.node_id not in calibration_data:
            calibration_data[minfo.node_id] = {}

        calib_min += soft_limit_mb
        calib_max -= soft_limit_mb
        if calib_max < calib_min:
            calib_min = calib_max  # Reverting back to the 'same value' to avoid bugs, due to small difference

        calibration_data[minfo.node_id][minfo.channel_id] = [calib_min, calib_max]

        yield (
            CalibrationStep.CALIBRATING_MAX,
            progress,
            f"Muscle at {vkey} saved with values: (min: {calib_min}, max: {calib_max})",
        )

    yield CalibrationStep.GENERATING, None, "Generating TOML snippet"

    toml_snippet = ""
    for node_id, muscles in calibration_data.items():
        toml_snippet += f"[pressure_sensors.{hex(node_id)}]"
        for channel_id, minmax in muscles.items():
            toml_snippet += f"\n{channel_id} = {minmax}"

        toml_snippet += "\n\n"

    yield CalibrationStep.DONE, 1.0, toml_snippet


@click.command()
@click.option(
    "--address", type=str, help="IP Address of a remote to perform muscle calibration on", required=True
)
@click.option(
    "--soft-limit-mb",
    type=int,
    default=50,
    help="Soft limit (pad) of calibration to avoid noise near edges (in milibars).",
)
@click.option(
    "--setpoint-mb",
    type=int,
    default=8500,
    help="Soft setpoint to calibrate to (in milibars). Muscles are always calibrated to the nearest achievable value",
)
@click.option(
    "--threshold-mb", type=int, default=50, help="A threshold for measurement acceptance (in milibars)."
)
@click.option("--samples", type=int, default=1000, help="Number of samples to extract edges (min, max).")
def run(address: str, soft_limit_mb: int, setpoint_mb: int, threshold_mb: int, samples: int):
    async def run_coro_iter():
        async with Client(address=address) as c:
            async for data in run_calibration(c, soft_limit_mb, setpoint_mb, threshold_mb, samples):
                print(data[-1])

    asyncio.run(run_coro_iter())


if __name__ == "__main__":
    run()
