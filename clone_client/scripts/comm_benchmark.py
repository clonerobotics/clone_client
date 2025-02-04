"""
Communication benchmark between client and the robot.
"""

import asyncio
import os
import socket
import sys
import time
from typing import AsyncIterable, Sequence

from clone_client.client import Client
from clone_client.utils import async_precise_interval

GOLEM_HOSTNAME = os.getenv("GOLEM_HOSTNAME", socket.gethostname())
GOLEM_ADDRESS = os.getenv("GOLEM_ADDRESS", None)
FREQUENCY = 100
SAMPLES = 1000


async def main() -> None:
    async with Client(address=GOLEM_ADDRESS, server=GOLEM_HOSTNAME) as client:
        start_freq = FREQUENCY
        pressures = [-1] * client.number_of_muscles

        for freq_add in range(0, 200, 10):
            freq = start_freq + freq_add
            expected_time = int(((1 / freq) * (SAMPLES // 100)) / 1e-9)
            tick = async_precise_interval(1 / freq, 0.9)
            print(f"Running at {freq} Hz")

            async def control_generator() -> AsyncIterable[Sequence[float]]:
                for run in range(100):

                    start = time.time_ns()
                    for sample in range(SAMPLES // 100):
                        await anext(tick)
                        yield pressures

                    elapsed = time.time_ns() - start

                    r = abs(expected_time / elapsed)
                    print(f"EL: {elapsed}, EX: {expected_time}, D: {(r) * 100:.2f}%")

                    if r < 0.985:
                        print(f"SLOW, Stopping at {run} run and {sample} sample, frequency: {freq}")
                        sys.exit(0)

                print(f"OK, frequency: {freq}")
                # Sleep to see if LED are gone which is another way to check if there is no queue on control BUS
                await asyncio.sleep(2)

            try:
                await client.stream_set_pressures(control_generator())
            except Exception as e:
                print(f"Error: {e}")


asyncio.run(main())
