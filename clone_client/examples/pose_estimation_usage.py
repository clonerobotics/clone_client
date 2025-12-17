import asyncio
from os import getenv

import numpy as np

from clone_client.client import Client
from clone_client.pose_estimation.pose_estimator import MagInterpolConfig


async def main() -> None:
    # pylint: disable=missing-function-docstring,line-too-long
    address = getenv("GOLEM_ADDRESS", "127.0.0.1")
    wrap_stream = getenv("WRAP_STREAM", "true").lower() == "true"
    async with Client(
        address=address,
        tunnels_used=Client.TunnelsUsed.STATE,
        additional_config=Client.Config(maginterp_config=MagInterpolConfig(filter_avg_samples=16)),
    ) as client:
        print("Connected to client")
        if wrap_stream:
            async for tele_ext in client.state_store.telemetry_stream_extend(
                client.state_store.subscribe_telemetry()
            ):
                print("\n" * 100)
                for name in tele_ext.qpos:
                    print(
                        f"{name:<20}: "
                        f"{np.array2string(tele_ext.qpos[name].as_quat(), formatter={'float_kind': lambda x: f'{x: .3f}'}):<20} "
                        f"{np.array2string(tele_ext.qvel[name], formatter={'float_kind': lambda x: f'{x: .3f}'}):<20}"
                    )
        else:
            async for tele in client.state_store.subscribe_telemetry():
                print("\n" * 100)
                tele_ext = client.state_store.telemetry_extend(tele)
                for name in tele_ext.qpos:
                    print(
                        f"{name:<20}: "
                        f"{np.array2string(tele_ext.qpos[name].as_quat(), formatter={'float_kind': lambda x: f'{x: .3f}'}):<20} "
                        f"{np.array2string(tele_ext.qvel[name], formatter={'float_kind': lambda x: f'{x: .3f}'}):<20}"
                    )


asyncio.run(main())
