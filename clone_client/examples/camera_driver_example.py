import asyncio
import logging
import os

from clone_client.camera_driver.client import CameraDriverClient
from clone_client.camera_driver.config import CameraDriverClientConfig

L = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    cfg = CameraDriverClientConfig()

    L.info("Connecting to camera driver at %s", cfg.grpc_addr)
    client = CameraDriverClient(cfg.grpc_addr, cfg)

    config_str = await client.get_config()
    print("=== CameraDriver config ===")
    print(config_str)
    print()

    streams = await client.list_streams()
    print("=== Streams ===")
    print(streams)
    print()
    await asyncio.sleep(1)

    if not streams:
        print("No streams reported by camera driver; exiting.")
        return

    stream_id = streams[0]
    print(f"Using stream_id={stream_id!r} for sink operations")

    demo_address = "239.0.0.1"
    demo_port = 5000
    demo_iface = "eth0"

    print(f"Adding sink {demo_address}:{demo_port} iface={demo_iface!r}")
    await client.add_sink(
        stream_id=stream_id,
        address=demo_address,
        port=demo_port,
        multicast_iface=demo_iface,
    )
    await asyncio.sleep(1)

    sinks = await client.list_sinks(stream_id)
    print("=== Sinks after AddSink ===")
    for s in sinks:
        print(f"- {s.address}:{s.port} iface={s.multicast_iface!r}")
    print()
    await asyncio.sleep(1)

    print("Removing the demo sink...")
    await client.remove_sink(stream_id, demo_address, demo_port)

    sinks_after_remove = await client.list_sinks(stream_id)
    print("=== Sinks after RemoveSink ===")
    for s in sinks_after_remove:
        print(f"- {s.address}:{s.port} iface={s.multicast_iface!r}")
    if not sinks_after_remove:
        print("(no sinks)")
    print()
    await asyncio.sleep(1)

    print("Removing all sinks for the stream")
    await client.remove_all_sinks(stream_id)
    sinks_final = await client.list_sinks(stream_id)
    print("=== Sinks after RemoveAllSinks ===")
    if not sinks_final:
        print("(no sinks)")
    else:
        for s in sinks_final:
            print(f"- {s.address}:{s.port} iface={s.multicast_iface!r}")
    print()

    await asyncio.sleep(1)

    print("List sinks after remove all")
    sinks = await client.list_sinks(stream_id)
    print("=== Sinks after Remove all ===")
    for s in sinks:
        print(f"- {s.address}:{s.port} iface={s.multicast_iface!r}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
