import asyncio

from clone_client.client import Client
from clone_client.kinematics.prototyping import utils
from clone_client.kinematics.prototyping.utils import FloatPrinter


async def main() -> None:

    async with Client(address="127.0.0.1", tunnels_used=Client.TunnelsUsed.STATE) as client:

        print("Getting system info")
        imus_mapping = await utils.get_imu_nodes_mapping(client)
        print(imus_mapping)

        print("Subscribing to telemetry")
        await asyncio.sleep(1.0)

        async for telemetry in client.subscribe_telemetry():
            imu_data = telemetry.imu
            imu_data_mapping = {item.node_id: item for item in imu_data}
            print(imu_data_mapping)

            rots = utils.rots_relative_from_telemetry(telemetry, imus_mapping)

            print("\n" * 100)
            for node_id, (rot_mine, rot_parent, rot_rel) in rots.items():
                print(f"Received quats from node {node_id}:")
                print(f"\t{"mine":10s}{list(map(FloatPrinter, rot_mine.as_quat()))}")
                if rot_parent is not None:
                    print(f"\t{"parent":10s}{list(map(FloatPrinter, rot_parent.as_quat()))}")
                else:
                    print("\t[ROOT]")
                if rot_rel is not None:
                    print(f"\t{"relative":10s}{list(map(FloatPrinter, rot_rel.as_quat()))}")
                else:
                    print("\t[ROOT]")
                print()


asyncio.run(main())
