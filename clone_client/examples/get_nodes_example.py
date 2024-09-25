import asyncio

from clone_client.client import Client


async def main() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    async with Client(address="127.0.0.1") as client:

        await asyncio.sleep(1)
        print(f"{await client.get_all_nodes()=}")
        print(f"{await client.get_all_nodes(True)=}")
        print(f"{await client.get_controlline_nodes()=}")
        print(f"{await client.get_controlline_nodes(True)=}")
        print(f"{await client.get_telemetryline_nodes()=}")
        print(f"{await client.get_telemetryline_nodes(True)=}")


asyncio.run(main())
