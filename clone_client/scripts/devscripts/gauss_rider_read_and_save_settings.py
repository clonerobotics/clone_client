import asyncio
from io import StringIO
from os import environ
from pathlib import Path

from clone_client.config import CONFIG
from clone_client.hw_driver.client import HWDriverClient, HWDriverClientConfig
from clone_client.magnet import CalibrationDataRaw, GaussCalculator

# TODO: enum with product ID should be transferred and used
PROD_ID_GAUSS_RIDER = 15


async def fetch_gauss_riders_ids(client: HWDriverClient) -> set[int]:
    print("Retriving least of nodes")
    nodes = await client.get_nodes()
    print(f"Retrived nodes: {nodes}")
    nodes_flat = [node for bus_name, bus_nodes in nodes.nodes.items() for node in bus_nodes.nodes]
    gauss_riders = {node.node_id for node in nodes_flat if node.product_id == PROD_ID_GAUSS_RIDER}
    print(f"GaussRiders found: {gauss_riders}, len: {len(gauss_riders)}")
    return gauss_riders


async def fetch_all_calibration_data(address: str) -> dict[int, CalibrationDataRaw]:
    client = HWDriverClient(address, HWDriverClientConfig())
    await client.channel_ready()
    gauss_riders = await fetch_gauss_riders_ids(client)
    gauss_settings = await client.get_gauss_rider_spec_settings()
    if gauss_riders.difference(gauss_settings.keys()):
        raise ValueError("Fetching failure, try again")
    return {
        nodeid: CalibrationDataRaw.from_gauss_spec_settings(spec_settings)
        for nodeid, spec_settings in gauss_settings.items()
    }


def save_calibration_data(calib_data: dict[int, CalibrationDataRaw], dir_name: str) -> None:
    path = Path(dir_name)
    if path.exists() and not path.is_dir():
        raise RuntimeError(f"{dir_name} exists and is not a directory")
    if not path.exists():
        path.mkdir()
    for nodeid, calib in calib_data.items():
        filepath = f"{path.absolute()}/gauss_rider_raw_calib.{nodeid}.json"
        calib.save(filepath)
    print("Saved!")


def test_calibration_data_load(dir_name: str) -> dict[int, CalibrationDataRaw]:
    path = Path(dir_name)
    calibs = {}
    for file in path.iterdir():
        print("found file: ", file.name)
        constant, node_id, suffix = file.name.split(".")
        if constant != "gauss_rider_raw_calib" or suffix != "json":
            raise RuntimeError("Invalid name")
        calibs[int(node_id)] = CalibrationDataRaw.load(str(file))
    return calibs


def test_calculator_creators(calib_data: dict[int, CalibrationDataRaw]) -> dict[int, GaussCalculator]:
    return {node_id: GaussCalculator(calib) for node_id, calib in calib_data.items()}


async def main() -> None:
    print("Start")
    try:
        address = environ["GOLEM_ADDRESS"]
    except KeyError:
        print("`GOLEM_ADDRESS` must be set")
        return
    if ":" not in address:
        address = f"{address}:{CONFIG.communication.hw_driver_service.default_port}"
    calib_data = await fetch_all_calibration_data(address)
    save_calibration_data(calib_data, "./fetched_calibration")
    calib_data_loaded = test_calibration_data_load("./fetched_calibration")
    if calib_data_loaded.keys() != calib_data.keys():
        raise RuntimeError("Loaded calibration data do not match saved ones")
    print(calib_data_loaded)
    print(test_calculator_creators(calib_data_loaded))
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
