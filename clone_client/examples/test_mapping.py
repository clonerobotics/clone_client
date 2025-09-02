import asyncio
import os
import socket

from clone_client.client import Client

GOLEM_HOSTNAME = os.getenv("GOLEM_HOSTNAME", socket.gethostname())
GOLEM_ADDRESS = os.getenv("GOLEM_ADDRESS", None)


async def main():
    async with Client(address=GOLEM_ADDRESS, server=GOLEM_HOSTNAME) as client:
        await client.set_pressures([0.0] * client.number_of_muscles)
        await asyncio.sleep(3)

        info = await client.get_system_info()

        for muscle_name, muscle_info in info.muscles.items():
            idx = client.muscle_idx(muscle_name)
            print(f"Muscle {muscle_name}")
            print(
                f"NodeID: {muscle_info.node_id}, ChannelID: {muscle_info.channel_id}, Index: {muscle_info.index}"
            )
            assert idx == muscle_info.index

            for act in [100, -100]:
                impulses: list[int | None] = [-100] * client.number_of_muscles
                impulses[idx] = act
                await client.set_pressures(impulses)
                await asyncio.sleep(1)
                tele = await client.get_telemetry()
                print(f"Pressure: {round(tele.sensor_data.pressures[idx], 3)}")


if __name__ == "__main__":
    asyncio.run(main())
