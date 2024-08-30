import asyncio
import logging
import os
import random
from socket import gethostname
from typing import List, Optional

from clone_client.client import Client
from clone_client.controller.proto.controller_pb2 import Pulse, PulseType, PulseValue

HOSTNAME = os.environ.get("HOSTNAME", gethostname())


async def api_run() -> None:
    logging.basicConfig(level=logging.INFO)
    async with Client(HOSTNAME) as client:
        # Get the controller configuration
        config = await client.get_controller_config()
        hand_info = await client.get_system_info()
        print(hand_info)
        if config.use_pump:
            # Start the water pump and wait for the desired pressure to be reached
            # before doing anything else.
            await client.start_waterpump()
            await client.wait_for_desired_pressure()

        for _ in range(int(1e3)):
            # Generate random impulses for all muscles
            # Value is relative to the muscle's maximum impulse (config.max_impulse_duration_ms)
            # 1.0 is the maximum impulse configured for the controller
            actions: List[Optional[float]] = [random.uniform(-1, 1) for _ in range(client.number_of_muscles)]

            # Set one muscle to None to ignore it
            actions[0] = None

            # Send actions to the controller
            # await client.set_muscles(actions)

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

            # await asyncio.sleep(config.max_impulse_duration_ms / 1000)

            # Get current pressures after actuation
            print("Single request telemetry")
            telemetry = await client.get_telemetry()
            print("Pressures", telemetry.pressures)
            print("IMU", telemetry.imu)
            if len(telemetry.pressures) == client.number_of_muscles:
                # Check specific muscle pressure
                muscle_name = client.muscle_name(0)
                index_extensor_index = client.muscle_idx(muscle_name)
                index_extensor_pressure = telemetry.pressures[index_extensor_index]
                print(f"{muscle_name} pressure: {index_extensor_pressure}")

            # Subscribe to telemetry updates
            count = 0
            async for telemetry in client.subscribe_telemetry():
                print("Telemetry", telemetry.pressures, telemetry.imu)

                count += 1
                if count > 150:
                    break

            await asyncio.sleep(1)

        # Loose all the muscles
        await client.loose_all()

        # Optionally stop water pump after the job is done
        await client.stop_waterpump()


if __name__ == "__main__":
    asyncio.run(api_run())
