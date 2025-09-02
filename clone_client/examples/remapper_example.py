"""Run with 'dry' as an argument to conduct dry tests. Otherwise this program
will try to connect to a client.
"""

import asyncio
import random

from clone_client.client import Client
from clone_client.remapper import Remapper


async def run_with_living_client() -> None:
    """Connect with a client, obtain remote ordering and create a Remapper
    Then map and remap a test vector.
    Subsequently, after 3 seconds start receiving telemetry from the client
    and reshuffle received pressures.
    """

    # Connect with a golem station
    async with Client(address="/run/clone") as client:

        # Obtain system info currently used by the station and get an ordering
        await client.get_system_info()
        remote_ordering = Remapper.swap_ordering(client.muscle_order)

        # Create local ordering by changing the remote one:
        local_ordering = remote_ordering.copy()
        local_ordering["muscle0"], local_ordering["muscle1"] = (
            local_ordering["muscle1"],
            local_ordering["muscle0"],
        )
        print(f"{remote_ordering=}")
        print(f"{local_ordering=}")
        remapper = Remapper(remote_ordering, local_ordering)

        # Or craete an ordering from a mapping file:
        # local_muscle_mapping = StringIO(
        #     """
        #     [
        #         {"name": "muscle0", "valve_address": "0x15:0"},
        #         {"name": "muscle1", "valve_address": "0x15:1"},
        #         {"name": "muscle2", "valve_address": "0x15:2"},
        #         {"name": "muscle3", "valve_address": "0x15:3"},
        #         {"name": "muscle4", "valve_address": "0x15:4"},
        #         {"name": "muscle5", "valve_address": "0x15:5"},
        #         {"name": "muscle6", "valve_address": "0x15:6"},
        #         {"name": "muscle7", "valve_address": "0x15:7"},
        #         {"name": "muscle8", "valve_address": "0x15:8"},
        #         {"name": "muscle9", "valve_address": "0x15:9"}
        #     ]
        #     """
        # )
        # remapper = Remapper(remote_ordering, local_muscle_mapping)

        vec = [float(i) for i in range(10)]
        print(f"{vec=}")
        vec_to_remote = remapper.local_to_remote(vec)
        vec_from_remote = remapper.remote_to_local(vec)
        print(f"{vec_to_remote=}")
        print(f"{vec_from_remote=}")
        revec_to_remote = remapper.remote_to_local(vec_to_remote)
        revec_from_remote = remapper.local_to_remote(vec_from_remote)
        print(f"{revec_to_remote=}")
        print(f"{revec_from_remote=}")

        await asyncio.sleep(3.0)
        async for tele in client.subscribe_telemetry():
            print("\n" * 100)
            pressures_from_remote = tele.sensor_data.pressures
            print(f"{pressures_from_remote=}")
            pressures_from_remote_remapped = remapper.remote_to_local(pressures_from_remote)
            print(f"{pressures_from_remote_remapped=}")
            pressures_to_set = [random.uniform(0.0, 0.2) for _ in range(client.number_of_muscles)]
            print(f"{pressures_to_set=}")
            pressures_to_set_remapped = remapper.local_to_remote(pressures_to_set)
            print(f"{pressures_to_set_remapped=}")
            await client.set_pressures(pressures_to_set_remapped)


if __name__ == "__main__":
    asyncio.run(run_with_living_client())
