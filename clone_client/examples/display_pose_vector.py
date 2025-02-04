import argparse
import asyncio
from math import degrees

from clone_client.client import Client


async def main() -> None:
    async with Client(address=args.address, tunnels_used=Client.TunnelsUsed.STATE) as client:
        # This is even simpler example, the only thing which is done over here is subscribing to telemetry.
        # May be used for telemetry debug.

        print("Subscribing to pose estimation")

        async for pose_vec in client.subscribe_pose_vector():
            print()
            print([degrees(q) for q in pose_vec] if args.degrees else pose_vec)


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "-a", "--address", help="IP or UNIX-socket address of a running golem system", default="/run/clone"
)
parser.add_argument(
    "-d", "--degrees", help="Display angles in degrees instead of radians", action="store_true"
)

args = parser.parse_args()

asyncio.run(main())
