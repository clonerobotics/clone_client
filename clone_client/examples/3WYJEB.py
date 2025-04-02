import asyncio
import sys
from typing import Optional

from scipy.spatial.transform import Rotation as R

from clone_client.client import Client


async def main_only_tele() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    async with Client(address="/run/clone", tunnels_used=Client.TunnelsUsed.STATE) as client:
        # async with Client(address="192.168.99.69") as client:

        print(f"{await client.get_system_info(True)}")
        i = 0
        tele_stream = client.subscribe_telemetry()
        r_thorax0: Optional[R] = None
        async for tele in tele_stream:
            if i < 50:
                i += 1
                continue
            i = 0
            imu_data = tele.imu
            imu_rs = {imu.node_id: R.from_quat([imu.x, imu.y, imu.z, imu.w]) for imu in imu_data}
            r_thorax = imu_rs[69]
            # if r_thorax0 is None:
            #     r_thorax0 = r_thorax
            #     continue
            # r_thorax_since_beginning = r_thorax0.inv() * r_thorax
            print(f'\n\n\n\n\n{r_thorax.as_euler("XYZ", degrees=True)}')


asyncio.run(main_only_tele())
