import asyncio
import logging

from clone_client.client import Client

logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    print("IMU info functions test")
    async with Client(address="/run/clone") as client:
        print("Connected with services")

        print(f"{client.number_of_imus=}")
        print(f"{client.imu_index_by_id(0x42)=}")
        print(f"{client.imu_index_by_name('IMU11')=}")
        try:
            print(f"{client.imu_index_by_id(0x88)=}")
        except KeyError:
            print("No IMU of ID 0x88")
        try:
            print(f"{client.imu_index_by_name('name')=}")
        except KeyError:
            print("No IMU of name 'name'")
        print(f"{client.imu_name(0)=}")
        print(f"{client.imu_id(0)=}")
        try:
            print(f"{client.imu_name(123)=}")
        except KeyError:
            print("No IMU of index 99")
        try:
            print(f"{client.imu_id(123)=}")
        except KeyError:
            print("No IMU of index 123")
        print(f"{client.imu_order()=}")
        print(f"{client.imu_info(0x42)=}")
    print("End of test")


asyncio.run(main())
