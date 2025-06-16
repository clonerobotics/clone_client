import asyncio

from clone_client.client import Client

DECIM_COEF = 5


async def main() -> None:

    async with Client(address="192.168.99.240", tunnels_used=Client.TunnelsUsed.STATE) as client:
        # This is even simpler example, the only thing which is done over here is subscribing to telemetry.
        # May be used for telemetry debug.

        print("Subscribing to telemetry")
        i = 0
        async for telemetry in client.subscribe_telemetry():
            if i < DECIM_COEF:
                i += 1
                continue
            i = 0

            print("\n" * 100)
            print(telemetry)


asyncio.run(main())
