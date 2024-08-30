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
from clone_client.controller.proto.controller_pb2 import ControllerRuntimeConfig

NO_READINGS = 5
HOSTNAME = os.getenv("CLONE_HOSTNAME", socket.gethostname())


def denormalize_value(normalized_value: float, original_min: int = 460, original_max: int = 1600) -> int:
    """
    Denormalizes a value that was normalized between 0 and 1 back to its original range,
    allowing for values slightly below 0 and above 1 due to sensor inaccuracies.

    :param normalized_value: The normalized value (can be slightly < 0 or > 1)
    :param original_min: The minimum value of the original range (default is 460)
    :param original_max: The maximum value of the original range (default is 1600)
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

    impulses: list[float | None] = [None] * client.number_of_muscles
    impulses[index] = 2000 / controller_config.max_impulse_duration_ms * activation
    await client.set_impulses(impulses)
    await asyncio.sleep(2.5)

    for _ in range(NO_READINGS):
        await asyncio.sleep(0.05)
        telemetry = await client.get_telemetry()
        yield denormalize_value(telemetry.pressures[index], calib_min, calib_max)


async def calibrate() -> None:
    """Start calibration process of pressure sensors readings"""

    logging.basicConfig(level=logging.INFO)
    calibration_data = []

    async with Client(HOSTNAME) as client:
        await client.loose_all()
        await asyncio.sleep(3)

        controller_config = await client.get_controller_config()
        hand_info = await client.get_system_info()

        for i in range(client.number_of_muscles):
            mname = client.muscle_name(i)
            calib_min = hand_info.calibration_data.pressure_sensors[i].min
            calib_max = hand_info.calibration_data.pressure_sensors[i].max
            aiter_max = activate_muscle(
                client, i, controller_config, calib_min=calib_min, calib_max=calib_max, activation=1
            )

            aiter_min = activate_muscle(
                client, i, controller_config, calib_min=calib_min, calib_max=calib_max, activation=-1
            )

            mmax = max([x async for x in aiter_max])
            mmin = min([x async for x in aiter_min])

            logging.info(
                "Muscle %s: min=%d, max=%d. (Calibration drift: min=%d, max=%d)",
                mname,
                mmin,
                mmax,
                calib_min - mmin,
                calib_max - mmax,
            )

            calibration_data.append([mmin, mmax])

        logging.info("Done. Save the data to 'calibration.json' file and restart the server")
        print(calibration_data)


if __name__ == "__main__":
    asyncio.run(calibrate())
