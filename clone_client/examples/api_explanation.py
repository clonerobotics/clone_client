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
        config = await client.controller.get_controller_config()
        system_info = await client.state_store.get_system_info()

        # System info includes muscle mapping, imu mapping and calibration data for pressure sensors
        print(system_info)

        if config.use_pump:
            # Start the water pump and wait for the desired pressure to be reached
            # before doing anything else.
            await client.controller.start_waterpump()
            await client.controller.wait_for_desired_pressure()

        await client.controller.lock_all()  # Reset control
        await client.controller.loose_all()  # Loose muscles
        await asyncio.sleep(3)

        # Set impulses
        for _ in range(int(10)):
            # Generate random impulses for all muscles
            # Value is relative to the muscle's maximum impulse (config.max_impulse_duration_ms)
            # 1.0 is the maximum impulse configured for the controller
            actions: List[Optional[float]] = [
                random.uniform(-1, 1) for _ in range(client.state_store.number_of_muscles)
            ]

            # Set one muscle to None to ignore it
            actions[0] = None

            # Send actions to the controller
            await client.controller.set_impulses(actions)

            # Sleep for the maximum impulse duration to prevent impulse overlaping
            await asyncio.sleep(
                (config.max_impulse_duration_ms / 1000) * max(abs(act) for act in actions if act is not None)
            )

        await client.controller.lock_all()  # Reset control

        # Set pulses
        for _ in range(int(10)):
            # Generate random pulse for one muscle (oscilations)
            # Keep None on the rest of the muscles to ignore setting them
            pulses = [Pulse(value=None)] * client.state_store.number_of_muscles
            pulses[0] = Pulse(
                value=PulseValue(
                    ctrl_type=random.choice([PulseType.IN, PulseType.OUT]),
                    pulse_len_ms=random.randint(5, 300),
                    delay_len_ms=random.randint(5, 300),
                    duration_ms=random.randint(1000, 3000),
                )
            )

            await client.controller.set_pulses(pulses)
            await asyncio.sleep(1)  # Sleep for the pulse duration

        await client.controller.lock_all()  # Reset control

        # Set pressures
        for _ in range(int(10)):
            # Generate random pressure activations for all muscles
            # Limit the maximum pressure to 0.2 (20% of the maximum pressure) to avoid hardware strain
            pressures = [random.uniform(0, 0.2) for _ in range(client.state_store.number_of_muscles)]
            await client.controller.set_pressures(pressures)

            # Sleep to let the muscles actuate
            await asyncio.sleep(1)

        await client.controller.lock_all()  # Reset control

        # Stream pressures
        async def pressure_stream_generator() -> AsyncIterable[Sequence[float]]:
            interval = async_precise_interval(1 / 10)  # 10 Hz
            for _ in range(100):
                await anext(interval)
                pressures = [random.uniform(0, 0.2) for _ in range(client.state_store.number_of_muscles)]
                yield pressures

        try:
            await client.controller.stream_set_pressures(pressure_stream_generator())
        except RpcError as e:
            # Stream at the end can raise an error with code CANCELLED.
            # This is expected behaviour and should be handled by the client.
            print(e)

        # Get telemetry
        telemetry = await client.state_store.get_telemetry()

        print("Pressures", telemetry.sensor_data.pressures)
        if len(telemetry.sensor_data.pressures) == client.state_store.number_of_muscles:
            # Check specific muscle pressure
            muscle_name = client.state_store.muscle_name(0)
            index_extensor_index = client.state_store.muscle_idx(muscle_name)
            index_extensor_pressure = telemetry.sensor_data.pressures[index_extensor_index]
            print(f"{muscle_name} pressure: {index_extensor_pressure}")

        # Subscribe to telemetry updates
        count = 0
        async for telemetry in client.state_store.subscribe_telemetry():
            print("Telemetry", telemetry.sensor_data.pressures)

            count += 1
            if count > 150:
                break

        # Loose all the muscles
        await client.controller.loose_all()

        # Optionally stop water pump after the job is done
        if config.use_pump:
            await client.controller.stop_waterpump()


if __name__ == "__main__":
    asyncio.run(api_run())
