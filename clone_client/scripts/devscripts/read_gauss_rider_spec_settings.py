"""Read calibration settings of GaussRiders. As an example and for testing."""

import asyncio
from os import environ

from clone_client.config import CONFIG
from clone_client.hw_driver.client import HWDriverClient, HWDriverClientConfig
from clone_client.magnet import CalibrationDataRaw, GaussCalculator


async def main() -> None:
    try:
        address = environ["GOLEM_ADDRESS"]
    except KeyError:
        print("`GOLEM_ADDRESS` must be set")
        return
    if ":" not in address:
        address = f"{address}:{CONFIG.communication.hw_driver_service.default_port}"
    client = HWDriverClient(address, HWDriverClientConfig())
    await client.channel_ready()
    gauss_settings = await client.get_gauss_rider_spec_settings()
    calib_data_raw = CalibrationDataRaw.from_gauss_spec_settings(gauss_settings[0x61])
    calib_data_raw.save("calibration-data.json")
    calib_data_raw = CalibrationDataRaw.load("calibration-data.json")
    config = GaussCalculator.Config()
    calc = GaussCalculator(config=config, calibration=calib_data_raw)
    print(gauss_settings)
    print(calib_data_raw)
    print(calc)


if __name__ == "__main__":
    asyncio.run(main())
