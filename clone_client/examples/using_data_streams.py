import asyncio
import os
import socket
from typing import AsyncIterable, Sequence

from grpc import RpcError

from clone_client.client import Client
from clone_client.utils import async_precise_interval

GOLEM_HOSTNAME = os.getenv("GOLEM_HOSTNAME", socket.gethostname())
GOLEM_ADDRESS = os.getenv("GOLEM_ADDRESS", None)
INDEX = 5
FREQ = 100
DEFAULT = -1.0
SAMPLES = FREQ // 2
ITERATIONS = 20


async def main() -> None:
    async with Client(server=GOLEM_HOSTNAME, address=GOLEM_ADDRESS) as client:
        await client.loose_all()
        await asyncio.sleep(3)
        # This is very basic example, usually a more complex solution would be needed to embedd the client
        # within existing solution like creating separated threads / tasks for streaming and buffering etc.

        async def control_generator() -> AsyncIterable[Sequence[float]]:
            tick = async_precise_interval(1 / FREQ, 0.9)
            for sample in range(ITERATIONS):
                pressures = [DEFAULT] * client.number_of_muscles
                for sample in range(SAMPLES):
                    await anext(tick)
                    pressures[INDEX] = sample / SAMPLES
                    yield pressures

                pressures = [DEFAULT] * client.number_of_muscles
                for sample in range(SAMPLES):
                    await anext(tick)
                    pressures[INDEX] = 1 - (sample / SAMPLES)
                    yield pressures

        try:
            print(f"Starting control stream for {client.muscle_name(INDEX)}")
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

            await asyncio.sleep(0.05)

        print("Unsubscribing from telemetry")


asyncio.run(main())
