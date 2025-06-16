import asyncio
import random
import sys
from typing import AsyncIterable

from clone_client.client import Client
from clone_client.valve_driver.proto.valve_driver_pb2 import (
    PinchValveCommands,
    PinchValveControl,
)


async def main_only_tele() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    async with Client(address="/run/clone") as client:
        # async with Client(address="192.168.99.69") as client:

        # print(f"{await client.get_system_info(True)}")
        # await asyncio.sleep(1)
        # print(f"{await client.get_all_nodes(True)=}")
        i = 0
        tele_stream = client.subscribe_telemetry()
        async for tele in tele_stream:
            # if i < 50:
            #     i += 1
            #     continue
            # i = 0
            print(tele)


async def main_with_tele() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    # async with Client(address="/run/clone") as client:
    async with Client(address="192.168.99.130") as client:

        print(f"{await client.get_system_info(True)}")
        await asyncio.sleep(1)
        print(f"{await client.get_all_nodes(True)=}")
        i = 0
        tele_stream = client.subscribe_telemetry()
        settings = [-0.1] * client.number_of_muscles
        # settings[0] = 0.01
        settings[5] = 0.01
        async for tele in tele_stream:
            if i < 50:
                i += 1
                continue
            i = 0
            print(tele)
            try:
                print("New settings: ", settings)
                await client.set_impulses(settings)
                print("Git")
                input("Press enter for next iteration")
            except KeyboardInterrupt as e:
                await client.lock_all()
                await client.loose_all()
                print(f"Exception: {e}")
                break


async def main() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    async with Client(address="/run/clone") as client:
        # Should raise ValueError
        # input("Positions, inlet fully open")
        # await client.send_pinch_valve_control(
        #     0x81, PinchValveControl.ControlMode.POSITIONS, PinchValveControl.PositionsType.INLET_FULLY_OPENED
        # )

        # while True:
        #     print('dupa')
        #     await client.send_pinch_valve_control(0x81, PinchValveControl.PRESSURE, 123)
        # input("Send angle 12")
        # await client.send_pinch_valve_control(0x81, PinchValveControl.ANGLE, 12)
        # input("Send angle 74")
        # await client.send_pinch_valve_control(0x81, PinchValveControl.ControlMode.ANGLE, 74)
        #
        # input("Send pressure (many)")
        # await client.send_many_pinch_valve_control(
        #     {0x81: PinchValveControl(mode=PinchValveControl.ControlMode.PRESSURE, value=0x44)}
        # )
        # input("Send pressures")
        # await client.set_pressures([.12])

        # async def gowno_stream() -> AsyncIterable[dict[int, PinchValveControl]]:
        #     while True:
        #         # value = random.randint(0, 360)
        #         value = PinchValveControl.PositionsType.BOTH_OPENED
        #         print(f"{value=}")
        #         yield {0x80: PinchValveControl(mode=PinchValveControl.ControlMode.POSITIONS, value=value)}
        #         input("Iter")
        #
        # input("Stream")
        # await client.stream_many_pinch_valve_control(gowno_stream())
        async def chuj():
            while True:
                value = [0.5]
                print("new value: ", value)
                await asyncio.sleep(1.0)
                yield value

        await client.stream_set_pressures(chuj())

        # await client.set_pressures([1.] * 10)

        # print(f"{await client.get_system_info(True)}")
        # await asyncio.sleep(1)
        # print(f"{await client.get_all_nodes(True)=}")
        # while True:
        #     try:
        #         settings = [0.0] * client.number_of_muscles
        #         settings[0] = 0.2
        #         await client.set_impulses([2 * random.random() - 1 for _ in range(client.number_of_muscles)])
        #         print("Git")
        #     except Exception as e:
        #         print(f"Exception: {e}")
        #     await asyncio.sleep(1.0)


if sys.argv.__len__() < 2:
    asyncio.run(main())
elif sys.argv[1].startswith("tele"):
    asyncio.run(main_with_tele())
elif sys.argv[1].startswith("only"):
    asyncio.run(main_only_tele())
