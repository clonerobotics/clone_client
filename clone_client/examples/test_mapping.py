import asyncio
import os
import socket

from clone_client.client import Client

GOLEM_HOSTNAME = os.getenv("GOLEM_HOSTNAME", socket.gethostname())
GOLEM_ADDRESS = os.getenv("GOLEM_ADDRESS", None)


async def main():
    async with Client(address=GOLEM_ADDRESS, server=GOLEM_HOSTNAME) as client:
        await client.loose_all()
        await asyncio.sleep(3)

        info = await client.get_system_info()

        for muscle_name, muscle_info in info.muscles.items():
            idx = client.muscle_idx(muscle_name)
            print(f"Muscle {muscle_name}")
            print(f"NodeID: {muscle_info.node_id}, ChannelID: {muscle_info.channel_id}")

            for act in [1, -1]:
                impulses: list[int | None] = [None] * client.number_of_muscles
                impulses[idx] = act
                await client.set_impulses(impulses)
                await asyncio.sleep(5)
                tele = await client.get_telemetry()
                print(f"Pressure: {round(tele.pressures[idx], 3)}")


if __name__ == "__main__":
    asyncio.run(main())
