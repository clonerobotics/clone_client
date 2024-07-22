import asyncio
import os
import socket

import psutil

from clone_client.client import Client

HOSTNAME = os.environ.get("GOLEM_SERVER_HOSTNAME", socket.gethostname())


def set_rt(prio: int, sched: int) -> None:
    """Set real-time process scheduler to prio and sched."""
    param = os.sched_param(prio)
    pid = psutil.Process().pid

    try:
        os.sched_setscheduler(pid, sched, param)
    except OSError:
        print("Failed to set real-time process scheduler to %u, priority %u" % (sched, prio))
    else:
        print("Process real-time priority set to: %u" % prio)


async def main():
    set_rt(99, os.SCHED_FIFO)
    async with Client(HOSTNAME) as client:
        await client.set_pressures([0] * client.number_of_muscles)
        await asyncio.sleep(1)

        for sample in range(1000):
            pressures = [sample / 1300] * client.number_of_muscles
            await client.set_pressures(pressures)
            print("Sent: ", pressures)
            rcv_pressures = await client.get_pressures()
            print("Rcv : ", rcv_pressures)
            await asyncio.sleep(1 / 100)


if __name__ == "__main__":
    asyncio.run(main())
