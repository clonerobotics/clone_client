import asyncio

from clone_client.client import Client


async def main() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    async with Client(address="192.168.99.146") as client:

        await asyncio.sleep(1)
        print(f"{await client.get_nodes()}")


asyncio.run(main())
