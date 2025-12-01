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

import numpy

from clone_client.client import Client
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


async def send_proportional(client: Client, node_id: int, channel_id: int, value: int) -> None:
    if value > 0:
        pvalue = PinchValveControl.INLET_FULLY_OPENED
        hvalue = HydraControlMessage.INLET_FULLY_OPENED
    elif value < 0:
        pvalue = PinchValveControl.OUTLET_FULLY_OPENED
        hvalue = HydraControlMessage.OUTLET_FULLY_OPENED
    else:
        pvalue = PinchValveControl.BOTH_CLOSED
        hvalue = HydraControlMessage.BOTH_CLOSED

    await client.controller.send_pinch_valve_control(
        node_id, control_mode=PinchValveControl.POSITIONS, value=pvalue
    )
    await send_hydra_single(client, node_id, channel_id, hvalue)


async def get_measurements(client: Client, samples: int) -> numpy.ndarray:
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

    return buf


async def calibrate():
    logging.basicConfig(level=logging.INFO)
    async with Client(address=GOLEM_ADDRESS, server=GOLEM_HOSTNAME) as client:
        controller_config = await client.controller.get_controller_config()
        info = await client.state_store.get_system_info()

        # Loose ALL, wait and read min values
        for _ in range(5):
            await client.controller.loose_all()

        meas = numpy.min(await get_measurements(client, samples=5000), axis=0)
        assert meas.shape == (client.state_store.number_of_muscles,)

        calibration_data = {}
        for muscle_name, muscle_info in info.muscles.items():
            if muscle_info.node_id not in calibration_data:
                calibration_data[muscle_info.node_id] = {}

            calib_min = info.calibration_data.pressure_sensors[muscle_info.index].min
            calib_max = info.calibration_data.pressure_sensors[muscle_info.index].max

            min_meas = denormalize_value(meas[muscle_info.index])
            calibration_data[muscle_info.node_id][muscle_info.channel_id] = [min_meas, calib_max]

            if MUSCLE_WHITELIST and muscle_name not in MUSCLE_WHITELIST:
                continue

            # Actuate one by one and read maxes
            for _ in range(ACT_TIME):
                if USE_PINCH_VALVES:
                    await send_proportional(client, muscle_info.node_id, muscle_info.channel_id, 1)
                    await asyncio.sleep(1)
                else:
                    impulses = [None] * client.state_store.number_of_muscles
                    impulses[muscle_info.index] = ACT_TIME * controller_config.max_impulse_duration_ms
                    await client.controller.set_impulses(impulses)
                    await asyncio.sleep(1)

            meas = numpy.max(await get_measurements(client, samples=5000), axis=0)
            assert meas.shape == (client.state_store.number_of_muscles,)

            calibration_data[muscle_info.node_id][muscle_info.channel_id][1] = denormalize_value(
                meas[muscle_info.index], calib_min, calib_max
            )

            logging.info(
                "Muscle %s: min=%s, max=%s",
                f"{hex(muscle_info.node_id)}:{muscle_info.channel_id} ({muscle_name})",
                calibration_data[muscle_info.node_id][muscle_info.channel_id][0],
                calibration_data[muscle_info.node_id][muscle_info.channel_id][1],
            )

            for _ in range(5):
                await client.controller.loose_all()

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

        for muscle_name, muscle_info in info.muscles.items():
            calib_min, calib_max = calibration_data[muscle_info.node_id][muscle_info.channel_id]
            calibration_data[muscle_info.node_id][muscle_info.channel_id] = [
                calib_min + soft_limt,
                calib_max - soft_limt,
            ]

        logging.info("Done. Save the data to 'calibration.toml' file and restart the server")

        for node_id, muscles in calibration_data.items():
            print(f"[pressure_sensors.{hex(node_id)}]")
            for channel_id, minmax in muscles.items():
                print(f"{channel_id} = {minmax}")


if __name__ == "__main__":
    asyncio.run(calibrate())
