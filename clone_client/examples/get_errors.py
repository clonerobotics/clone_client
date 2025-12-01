"""Example shows how to use `get_nodes` functionality"""

import asyncio
import ipaddress
import os
from pathlib import Path

from clone_client.client import Client, CONFIG
from clone_client.hw_driver.client import HWDriverClient, HWDriverClientConfig


async def get_errors_client(golem_address):  # type: ignore
    async with Client(
        address=golem_address, tunnels_used=Client.TunnelsUsed.STATE | Client.TunnelsUsed.HW_DRIVER
    ) as client:
        print("client connected")
        while True:
            if Client.TunnelsUsed.STATE in client.tunnels_used:
                state_store_errors = await client.state_store.get_errors()
                if state_store_errors is None:
                    print("`get_errors` disabled for the state-store")
                else:
                    print("State-store's errors:")
                    print(state_store_errors)
                    print(f"state-store recent error count: {len(state_store_errors)}")

            if Client.TunnelsUsed.CONTROLLER in client.tunnels_used:
                controller_errors = await client.controller.get_errors()
                if controller_errors is None:
                    print("`get_errors` disabled for the controller")
                else:
                    print("Controller's errors:")
                    print(controller_errors)
                    print(f"controller recent error count: {len(controller_errors)}")

            if Client.TunnelsUsed.HW_DRIVER in client.tunnels_used:
                hw_errors = await client.hw_driver.get_errors()
                if hw_errors.hw_driver_errors is None:
                    print("`get_errors` disabled for the hw-driver")
                else:
                    print(hw_errors)
                    print(f"hw-driver recent error count: {len(hw_errors.hw_driver_errors)}")
                    for bus_name, bus_errors in hw_errors.buses_errors.items():
                        if bus_errors is None:
                            print(f"bus {bus_name} did not send its errors")
                        else:
                            print(bus_name)
                            print(bus_errors)
                            print(f"bus {bus_name} recent error count: {len(bus_errors)}")
            await asyncio.sleep(1.0)


async def get_errors_hw_driver(golem_address):  # type: ignore
    if ":" not in golem_address:
        try:
            ipaddress.ip_address(golem_address)
            golem_address = f"{golem_address}:{CONFIG.communication.hw_driver_service.default_port}"
        except ValueError:
            golem_address = f"unix://{
                    Path(golem_address)
                    / Path(CONFIG.communication.hw_driver_service.default_unix_sock_name)
                    }"
    client = HWDriverClient(socket_address=golem_address, config=HWDriverClientConfig())
    await client.channel_ready()
    print("client connected")
    while True:
        errors = await client.get_errors()
        print(errors)
        if errors.hw_driver_errors is not None:
            print(f"hw-driver recent error count: {len(errors.hw_driver_errors)}")
            for bus_name, bus_errors in errors.buses_errors.items():
                if bus_errors is None:
                    print(f"bus {bus_name} did not send its errors")
                else:
                    print(f"bus {bus_name} recent error count: {len(bus_errors)}")
        await asyncio.sleep(1.0)


try:
    GOLEM_ADDRESS = os.environ.get("GOLEM_ADDRESS", "/tmp/")
    TEST_HW_DRIVER = os.environ.get("TEST_HW_DRIVER", "false").lower() == "true"
    if TEST_HW_DRIVER:
        asyncio.run(get_errors_hw_driver(GOLEM_ADDRESS))
    else:
        asyncio.run(get_errors_client(GOLEM_ADDRESS))
except KeyboardInterrupt:
    print("bye")
