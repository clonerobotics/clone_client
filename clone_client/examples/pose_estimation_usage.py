import asyncio
from os import getenv
from pprint import pprint

from clone_client.client import Client


async def main() -> None:
    address = getenv("GOLEM_ADDRESS", "127.0.0.1")
    show_names = getenv("SHOW_NAMES", "").lower() == "true"
    async with Client(
        address=address,
        tunnels_used=Client.TunnelsUsed.STATE,
        additional_config=Client.Config(maginterp_disable=False, maginterp_filter_avg_samples=16),
    ) as client:
        print("Connected to client")
        qpos_to_jnt_mapping = sorted(client.qpos_to_jnt_mapping.items())
        async for qpos_vec in client.subscribe_angles():
            print("\n" * 100)
            if show_names:
                for qpos, (jnt_name, axis_name) in qpos_to_jnt_mapping:
                    print(f"{jnt_name}.{axis_name}: {qpos_vec[qpos]}")
            else:
                pprint(qpos_vec)


asyncio.run(main())
