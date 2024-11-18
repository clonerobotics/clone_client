import asyncio

from clone_client.client import Client

FIELDS = ["w", "x", "y", "z", "ax", "ay", "az"]
DECIM_COEF = 5


async def main() -> None:

    async with Client(address="127.0.0.1", tunnels_used=Client.TunnelsUsed.STATE) as client:
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

            for imu in telemetry.imu:
                print(f"nodeid: {imu.node_id}")
                for field in FIELDS:
                    print(f"\t{field:2s}: {getattr(imu, field):+.6f}")


asyncio.run(main())
