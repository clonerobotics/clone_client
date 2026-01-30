import asyncio
import os

from clone_client.client import Client

DECIM_COEF = 5
GOLEM_ADDRESS = os.environ.get("GOLEM_ADDRESS", "127.0.0.1")


async def main() -> None:

    async with Client(address=GOLEM_ADDRESS, tunnels_used=Client.TunnelsUsed.STATE) as client:
        # This is even simpler example, the only thing which is done over here is subscribing to telemetry.
        # May be used for telemetry debug.

        print("Subscribing to telemetry")
        i = 0
        async for telemetry in client.state_store.subscribe_telemetry():
            if i < DECIM_COEF:
                i += 1
                continue
            i = 0

            print("\n" * 100)
            print(telemetry)


asyncio.run(main())
