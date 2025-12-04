import asyncio
from os import getenv
from pprint import pprint

from clone_client.client import Client
from clone_client.pose_estimation.pose_estimator import MagInterpolConfig


async def main() -> None:
    address = getenv("GOLEM_ADDRESS", "127.0.0.1")
    show_names = getenv("SHOW_NAMES", "true").lower() == "true"
    wrap_stream = getenv("WRAP_STREAM", "true").lower() == "true"
    async with Client(
        address=address,
        tunnels_used=Client.TunnelsUsed.STATE,
        additional_config=Client.Config(
            maginterp_config=MagInterpolConfig(disable=False, filter_avg_samples=16)
        ),
    ) as client:
        print("Connected to client")
        qpos_to_jnt_mapping = sorted(client.state_store.qpos_to_jnt_mapping.items())
        if wrap_stream:
            async for tele_ext in client.state_store.telemetry_stream_extend(
                client.state_store.subscribe_telemetry()
            ):
                print("\n" * 100)
                if show_names:
                    for qpos, (jnt_name, axis_name) in qpos_to_jnt_mapping:
                        print(
                            f"{f'{jnt_name}.{axis_name}:':<20} {tele_ext.qpos[qpos].round(3):>10} "
                            f"{tele_ext.qvel[qpos].round(3):>10}"
                        )
                else:
                    pprint(tele_ext.qpos)
                    pprint(tele_ext.qvel)
        else:
            async for tele in client.state_store.subscribe_telemetry():
                print("\n" * 100)
                tele_ext = client.state_store.telemetry_extend(tele)
                if show_names:
                    for qpos, (jnt_name, axis_name) in qpos_to_jnt_mapping:
                        print(
                            f"{f'{jnt_name}.{axis_name}:':<20} {tele_ext.qpos[qpos].round(3):>10} "
                            f"{tele_ext.qvel[qpos].round(3):>10}"
                        )
                else:
                    pprint(tele_ext.qpos)
                    pprint(tele_ext.qvel)


asyncio.run(main())
