"""This example presents how pausing telemetry works. It prints telemetry for 3 seconds,
then it pauses it for another 3 seconds then resumes it and after another 3 seconds it exits"""

import asyncio

from clone_client.client import Client


async def print_telemetry(client: Client) -> None:
    async for tele in client.state_store.subscribe_telemetry():
        print(tele)


async def main() -> None:
    async with Client(
        address="/tmp", tunnels_used=Client.TunnelsUsed.STATE | Client.TunnelsUsed.HW_DRIVER
    ) as client:
        asyncio.create_task(print_telemetry(client))
        await asyncio.sleep(3)
        await client.hw_driver.pause_telemetry(True)
        await asyncio.sleep(3)
        await client.hw_driver.pause_telemetry(False)
        await asyncio.sleep(3)


asyncio.run(main())
print("BYE")
