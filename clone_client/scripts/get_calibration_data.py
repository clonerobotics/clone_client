"""
Get the calibration values (min and max) of the pressure sensors.
Uses current (or default) calibration data to calibrate it again based on the
returned pressure values.

Run it each time you want to calibrate the pressure sensors, i.e. pressure changed.
This should be implemented as a API call in the future for more automation.
"""

import asyncio
import logging
import os
import socket
from typing import AsyncIterator

from clone_client.client import Client
from clone_client.proto.controller_pb2 import ControllerRuntimeConfig

GOLEM_HOSTNAME = os.getenv("GOLEM_HOSTNAME", socket.gethostname())
GOLEM_ADDRESS = os.getenv("GOLEM_ADDRESS", None)
USE_PINCH_VALVES = os.getenv("USE_PINCH_VALVES", False)
NO_READINGS = 150
ACT_TIME = 3
SNAPSHOT_AT = 5

# Just paste the snapshot directly, who cares. Just not commit.
# list of [mmin, mmax] pairs
LOADED_SNAPSHOT: list[list[int]] = []

# Some muscles are bigger but that information is not known from the golem so it needs to be put manually
# Again, paste it here but don't commit.
# Dict of muscle index to contraction time in seconds
CONTRACTION_TIME: dict[int, int] = {}


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


async def activate_muscle(
    client: Client,
    index: int,
    controller_config: ControllerRuntimeConfig,
    calib_min: int,
    calib_max: int,
    activation: int,
) -> AsyncIterator[int]:
    """
    Increase pressure for the given muscle to the maximum
    """
    contraction_time = CONTRACTION_TIME.get(index, ACT_TIME)
    if not USE_PINCH_VALVES:
        impulses: list[float | None] = [None] * client.number_of_muscles
        impulses[index] = contraction_time * 1000 / controller_config.max_impulse_duration_ms * activation
    else:
        impulses: list[int] = [-1000] * client.number_of_muscles
        impulses[index] = 1000 * activation

    for _ in range(3):
        if not USE_PINCH_VALVES:
            await client.set_impulses(impulses)
        else:
            await client.set_pressures(pressures=impulses)
        await asyncio.sleep(((contraction_time) // 3))

    await asyncio.sleep(0.5)

    for _ in range(NO_READINGS):
        await asyncio.sleep(0.05)
        telemetry = await client.get_telemetry()
        yield denormalize_value(telemetry.sensor_data.pressures[index], calib_min, calib_max)


async def calibrate() -> None:
    """Start calibration process of pressure sensors readings"""

    logging.basicConfig(level=logging.INFO)

    async with Client(address=GOLEM_ADDRESS, server=GOLEM_HOSTNAME) as client:
        if not USE_PINCH_VALVES:
            await client.loose_all()
        else:
            await client.set_pressures([-1000] * client.number_of_muscles)
        await asyncio.sleep(3)

        controller_config = await client.get_controller_config()
        info = await client.get_system_info()

        # Prepare empty calibration data
        calibration_data = {}
        for muscle_name, muscle_info in info.muscles.items():
            if muscle_info.node_id not in calibration_data:
                calibration_data[muscle_info.node_id] = {}

            calibration_data[muscle_info.node_id][muscle_name] = [0, 0]

        for i, mname in sorted(client.muscle_order.items()):
            muscle_info = info.muscles[mname]
            try:
                if i not in CONTRACTION_TIME:
                    [mmin, mmax] = LOADED_SNAPSHOT[i]
                    logging.info("Using snapshot data for muscle %d: min=%d, max=%d", i, mmin, mmax)
                    calibration_data[muscle_info.node_id][mname] = [mmin, mmax]
                    continue
            except IndexError:
                pass

            logging.info("Calibrating muscle %s (%d)", mname, i)
            calib_min = info.calibration_data.pressure_sensors[i].min
            calib_max = info.calibration_data.pressure_sensors[i].max
            try:
                aiter_max = activate_muscle(
                    client, i, controller_config, calib_min=calib_min, calib_max=calib_max, activation=1
                )

                aiter_min = activate_muscle(
                    client, i, controller_config, calib_min=calib_min, calib_max=calib_max, activation=-1
                )

                mmax = max([x async for x in aiter_max])
                mmin = min([x async for x in aiter_min])
            except Exception as e:
                print(e)
                mmin = calib_min
                mmax = calib_max

            logging.info(
                "Muscle %s: min=%d, max=%d. (Calibration drift: min=%d, max=%d)",
                mname,
                mmin,
                mmax,
                calib_min - mmin,
                calib_max - mmax,
            )

            calibration_data[muscle_info.node_id][mname] = [mmin, mmax]
            if i > 0 and i % SNAPSHOT_AT == 0:
                logging.info("Here's a snapshot of calibration data (last muscle: %s (%d)): ", mname, i)
                print(calibration_data)

        logging.info("Raw calibration data after all iterations: ")
        print(calibration_data)

        print(
            """
            SOFT LIMIT:
            Soft limit is a way to compensate for the pressure sensor drift and noise.
            This does not solve the issue, but in a scenario when a maximum and/or minimum pressure
            happen to be a sparse noise value this helps making them more stable and
            always 'be seen' by the sensor.
        """
        )

        try:
            soft_limit = input("What soft limit you want to set (default: 50 milibar) ?: ")
            soft_limt = int(soft_limit)
        except ValueError:
            logging.warning("Invalid input, using default value of 50 milibar.")
            soft_limt = 50

        for i, mname in client.muscle_order.items():
            node_id = info.muscles[mname].node_id
            calib_min, calib_max = calibration_data[node_id][mname]
            calibration_data[node_id][mname] = [calib_min + soft_limt, calib_max - soft_limt]

        logging.info("Done. Save the data to 'calibration.toml' file and restart the server")

        for node_id, muscles in calibration_data.items():
            print(f"[pressure_sensors.{hex(node_id)}]")
            for mname, minmax in muscles.items():
                channel_id = info.muscles[mname].channel_id
                print(f"{channel_id} = {minmax}")


if __name__ == "__main__":
    asyncio.run(calibrate())
