import asyncio
import logging

from clone_client.client import Client

logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    async with Client(address="/run/clone") as client:
        await asyncio.sleep(1.0)

        print("Subscribing to telemetry")
        async for telemetry in client.state_store.subscribe_telemetry():
            print("\n" * 100)
            print(telemetry)


asyncio.run(main())
