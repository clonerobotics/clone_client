import asyncio
import csv
from collections import deque

from clone_client.client import Client

async def main(data: deque):
    print("main started")
    async with Client(address="/run/clone", tunnels_used=Client.TunnelsUsed.STATE) as client:
        print("client connected")
        async for tele in client.subscribe_telemetry():
            grs = {gr.node_id: gr for gr in tele.gauss_rider_data}
            s = grs[96].sensor
            a = [getattr(px, let) for px in s.pixels for let in 'xyz']
            print(a)
            data.append(a)

            

if __name__ == "__main__":
    data = deque()
    try:
        asyncio.run(main(data))
    except KeyboardInterrupt:
        with open("data.csv", 'w') as fp:
            writer = csv.writer(fp)
            writer.writerow(['px0.x', 'px0.y', 'px0.z', 'px1.x', 'px1.y', 'px1.z', 'px2.x', 'px2.y', 'px2.z', 'px3.x', 'px3.y', 'px3.z', ])
            writer.writerows(data)
    print("nara")
