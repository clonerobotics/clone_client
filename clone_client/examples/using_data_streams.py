import asyncio
from typing import AsyncIterable, Sequence

from grpc import RpcError

from clone_client.client import Client
from clone_client.utils import async_busy_ticker


async def main() -> None:
    async with Client(address="127.0.0.1") as client:
        # This is very basic example, usually a more complex solution would be needed to embedd the client
        # within existing solution like creating separated threads / tasks for streaming and buffering etc.
        async def control_generator() -> AsyncIterable[Sequence[float]]:
            for _ in range(1000):
                pressures = [0.0] * client.number_of_muscles
                async with async_busy_ticker(1 / 300):
                    yield pressures

        try:
            print("Starting control stream")
            await client.stream_set_pressures(control_generator())
        except RpcError as e:
            print(e)

        await asyncio.sleep(1)

        telemetry_count = 100
        print("Subscribing to telemetry")
        async for telemetry in client.subscribe_telemetry():
            print(telemetry)

            telemetry_count -= 1
            if telemetry_count == 0:
                break


asyncio.run(main())
