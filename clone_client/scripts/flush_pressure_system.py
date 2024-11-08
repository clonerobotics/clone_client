"""
Script to flush the entire pressure system with the dedicated medium.
This is useful when switching from air to water and vice versa.
"""

import asyncio
import os
import socket

from clone_client.client import Client

GOLEM_HOSTNAME = os.getenv("GOLEM_HOSTNAME", socket.gethostname())
GOLEM_ADDRESS = os.getenv("GOLEM_ADDRESS", None)
NO_FLUSHES = 100000
CONCURRENT_MUSCLES = 3
FLUSH_TIME = 0.3


async def flush() -> None:
    """
    Flush the pressure system with the dedicated medium
    """
    async with Client(address=GOLEM_ADDRESS, server=GOLEM_HOSTNAME) as client:
        await client.loose_all()
        await asyncio.sleep(3)
        impulses = [0] * client.number_of_muscles

        cursor = 0
        for _ in range(NO_FLUSHES):
            impulses = [0] * client.number_of_muscles
            impulses[cursor : CONCURRENT_MUSCLES + cursor] = [1] * CONCURRENT_MUSCLES
            await client.set_impulses(impulses)
            await asyncio.sleep(FLUSH_TIME)

            impulses[cursor : CONCURRENT_MUSCLES + cursor] = [-1] * CONCURRENT_MUSCLES
            await client.set_impulses(impulses)
            await asyncio.sleep(FLUSH_TIME)

            cursor += CONCURRENT_MUSCLES
            if cursor + CONCURRENT_MUSCLES >= client.number_of_muscles:
                cursor = 0


if __name__ == "__main__":
    asyncio.run(flush())
