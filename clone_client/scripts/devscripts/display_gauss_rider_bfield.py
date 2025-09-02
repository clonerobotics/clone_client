"""Script displays Bfield from a sensor (by default 0x61) calculate with use of full calibration"""

# NOTE: first use `read_gauss_rider_spec_settings.py` to fetch calibration data

import asyncio
from os import environ

from clone_client.client import Client
from clone_client.magnet import CalibrationDataRaw, gauss_rider_rewrap, GaussCalculator


async def main() -> None:
    try:
        address = environ["GOLEM_ADDRESS"]
    except KeyError:
        print("`GOLEM_ADDRESS` not set, trying locally")
        address = "/run/clone"

    calib_data_raw = CalibrationDataRaw.load("calibration-data.json")
    calc = GaussCalculator(calib_data_raw)
    async with Client(address=address, tunnels_used=Client.TunnelsUsed.STATE) as client:
        async for tele in client.subscribe_telemetry():
            gauss_map = {gr.node_id: gr for gr in tele.sensor_data.gauss_rider_data}
            b = calc.calculate_bfield([gauss_rider_rewrap(gauss_map[0x61])])
            print("\n" * 100)
            print(b)


if __name__ == "__main__":
    asyncio.run(main())
