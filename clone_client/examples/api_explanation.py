import asyncio
import os
from random import randint
from socket import gethostname

from clone_client.client import Client

HOSTNAME = os.environ.get("HOSTNAME", gethostname())


async def api_run() -> None:
    async with Client(HOSTNAME) as client:
        # Start the pressure generator and wait for the desired pressure to be reached
        # before doing anything else.
        await client.start_pressuregen()
        await client.wait_for_desired_pressure()

        for _ in range(int(1e3)):
            # Generate random actions, available values are [-1, 0, 1]. Floats are allowed, however they make no impact.
            actions = [randint(0, 2) - 1 for _ in range(client.number_of_muscles)]  # nosec

            # Send actions to the controller
            await client.set_muscles(actions)
            await asyncio.sleep(0.1)

            # Get current pressures after actuation
            pressures = await client.get_pressures()
            if pressures is None:
                raise RuntimeError("got empty pressures")

            print(pressures)

            # Check specific muscle pressure
            index_extensor_index = client.muscle_idx("index_extensor")
            index_extensor_pressure = pressures[index_extensor_index]
            print(f"index_extensor pressure: {index_extensor_pressure}")

        # Loose all the muscles
        await client.loose_all()

        # Optionally stop pressure generator after the job is done
        await client.stop_pressuregen()


if __name__ == "__main__":
    asyncio.run(api_run())
