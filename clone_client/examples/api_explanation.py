"""
This example demonstrates how to use the clone client API to interact with the controller.
"""

import asyncio
import logging
import os
import random
from socket import gethostname
from typing import AsyncIterable, List, Optional, Sequence

from grpc import RpcError

from clone_client.client import Client
from clone_client.proto.controller_pb2 import Pulse, PulseType, PulseValue
from clone_client.utils import async_precise_interval

HOSTNAME = os.environ.get("HOSTNAME", gethostname())
ADDRESS = os.environ.get("ADDRESS", "127.0.0.1")


async def api_run() -> None:
    logging.basicConfig(level=logging.INFO)
    async with Client(HOSTNAME, address=ADDRESS) as client:
        # Get the controller configuration
        config = await client.get_controller_config()
        system_info = await client.get_system_info()

        # System info includes muscle mapping, imu mapping and calibration data for pressure sensors
        print(system_info)

        if config.use_pump:
            # Start the water pump and wait for the desired pressure to be reached
            # before doing anything else.
            await client.start_waterpump()
            await client.wait_for_desired_pressure()

        await client.lock_all()  # Reset control
        await client.loose_all()  # Loose muscles
        await asyncio.sleep(3)

        # Set impulses
        for _ in range(int(10)):
            # Generate random impulses for all muscles
            # Value is relative to the muscle's maximum impulse (config.max_impulse_duration_ms)
            # 1.0 is the maximum impulse configured for the controller
            actions: List[Optional[float]] = [random.uniform(-1, 1) for _ in range(client.number_of_muscles)]

            # Set one muscle to None to ignore it
            actions[0] = None

            # Send actions to the controller
            await client.set_impulses(actions)

            # Sleep for the maximum impulse duration to prevent impulse overlaping
            await asyncio.sleep(
                (config.max_impulse_duration_ms / 1000) * max(abs(act) for act in actions if act is not None)
            )

        await client.lock_all()  # Reset control

        # Set pulses
        for _ in range(int(10)):
            # Generate random pulse for one muscle (oscilations)
            # Keep None on the rest of the muscles to ignore setting them
            pulses = [Pulse(value=None)] * client.number_of_muscles
            pulses[0] = Pulse(
                value=PulseValue(
                    ctrl_type=random.choice([PulseType.IN, PulseType.OUT]),
                    pulse_len_ms=random.randint(5, 300),
                    delay_len_ms=random.randint(5, 300),
                    duration_ms=random.randint(1000, 3000),
                )
            )

            await client.set_pulses(pulses)
            await asyncio.sleep(1)  # Sleep for the pulse duration

        await client.lock_all()  # Reset control

        # Set pressures
        for _ in range(int(10)):
            # Generate random pressure activations for all muscles
            # Limit the maximum pressure to 0.2 (20% of the maximum pressure) to avoid hardware strain
            pressures = [random.uniform(0, 0.2) for _ in range(client.number_of_muscles)]
            await client.set_pressures(pressures)

            # Sleep to let the muscles actuate
            await asyncio.sleep(1)

        await client.lock_all()  # Reset control

        # Stream pressures
        async def pressure_stream_generator() -> AsyncIterable[Sequence[float]]:
            interval = async_precise_interval(1 / 10)  # 10 Hz
            for _ in range(100):
                await anext(interval)
                pressures = [random.uniform(0, 0.2) for _ in range(client.number_of_muscles)]
                yield pressures

        try:
            await client.stream_set_pressures(pressure_stream_generator())
        except RpcError as e:
            # Stream at the end can raise an error with code CANCELLED.
            # This is expected behaviour and should be handled by the client.
            print(e)

        # Get telemetry
        telemetry = await client.get_telemetry()

        print("Pressures", telemetry.sensor_data.pressures)
        print("Magnetic", telemetry.sensor_data.magnetic_data)
        if len(telemetry.sensor_data.pressures) == client.number_of_muscles:
            # Check specific muscle pressure
            muscle_name = client.muscle_name(0)
            index_extensor_index = client.muscle_idx(muscle_name)
            index_extensor_pressure = telemetry.sensor_data.pressures[index_extensor_index]
            print(f"{muscle_name} pressure: {index_extensor_pressure}")

        # Subscribe to telemetry updates
        count = 0
        async for telemetry in client.subscribe_telemetry():
            print("Telemetry", telemetry.sensor_data.pressures, telemetry.sensor_data.magnetic_data)

            count += 1
            if count > 150:
                break

        # Loose all the muscles
        await client.loose_all()

        # Optionally stop water pump after the job is done
        if config.use_pump:
            await client.stop_waterpump()


if __name__ == "__main__":
    asyncio.run(api_run())
