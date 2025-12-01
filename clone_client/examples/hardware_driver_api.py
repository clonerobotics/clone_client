import asyncio
from ipaddress import ip_address
import os

from clone_client.client import CONFIG
from clone_client.exceptions import ClientError
from clone_client.hw_driver.client import HWDriverClient, HWDriverClientConfig


async def main() -> None:
    """Show new API of the hw-driver client"""
    golem_address = os.environ.get("GOLEM_ADDRESS", "127.0.0.1")
    node_to_ping = int(os.environ.get("PING_NODE", "0x61"), 0)
    bus_name = os.environ.get("BUS_NAME", "/dev/ttyTHS0")
    timeout_us = int(os.environ.get("TIMEOUT", "10000000"))

    if ":" not in golem_address:
        try:
            ip_address(golem_address)
            golem_address = f"{golem_address}:{CONFIG.communication.hw_driver_service.default_port}"
        except ValueError:
            golem_address = (
                f"unix://{golem_address}/{CONFIG.communication.hw_driver_service.default_unix_sock_name}"
            )

    client = HWDriverClient(socket_address=golem_address, config=HWDriverClientConfig())
    await client.channel_ready()
    print("Client connected")
    print()

    print("GetNodes run")
    nodes = await client.get_nodes()
    print(f"GetNodes returned:\n{nodes}")
    print()

    print("PingNode run")
    try:
        await client.ping_node(node_id=node_to_ping, bus_name=bus_name)
    except ClientError as e:
        print(f"Ping error: {e}")
    else:
        print("Ping OK")
    print()

    print("Discovery run")
    discovered_nodes = await client.discovery(
        bus_name=bus_name,
        timeout_us=timeout_us,
    )
    print(f"Discovered node ids: {discovered_nodes}")
    print()

    print("GetNodesSettings run")
    settings = await client.get_nodes_settings(bus_name=bus_name, node_ids=discovered_nodes)
    print(f"GetNodesSettings returned: {settings}")


asyncio.run(main())
