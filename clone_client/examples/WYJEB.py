import asyncio

from clone_client.client import Client


async def main() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    async with Client(address="/run/clone", tunnels_used=Client.TunnelsUsed.STATE) as client:

        aeee = await client.get_system_info(True)
        print(aeee)
        print()
        print(f"{client.jnt_to_qpos_mapping=}")
        print(f"{client.qpos_to_jnt_mapping=}")


asyncio.run(main())
