import asyncio
import random

from clone_client.client import Client


async def main() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    async with Client(address="/run/clone") as client:
        # async with Client(address="192.168.99.69") as client:

        await client.get_system_info(True)
        await asyncio.sleep(1)
        # print(f"{await client.get_all_nodes(True)=}")
        while True:
            await asyncio.sleep(0.005)
            try:
                settings = [0.0] * client.number_of_muscles
                settings[0] = 0.2
                await client.set_pressures(settings)
                print("Git")
            except Exception as e:
                print(f"Exception: {e}")


asyncio.run(main())
