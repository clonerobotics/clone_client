import argparse
import asyncio
from itertools import pairwise

parser = argparse.ArgumentParser()
parser.add_argument("kurwaaa", default="71-70", nargs="?")
key = parser.parse_args().kurwaaa

from collections import deque
import time

import dearpygui.dearpygui as dpg
from scipy.spatial.transform import Rotation as R

from clone_client.client import Client

# --- Global Data Storage for Plotting ---
data_time = deque([0.0], maxlen=100)
data_x = deque([], maxlen=100)
data_y = deque([], maxlen=100)
data_z = deque([], maxlen=100)
data_w = deque([], maxlen=100)

start_time = time.time()

tag = 0


def update_data(quat):
    """Update the global data lists with new quaternion values."""
    current_time = time.time() - start_time

    # Append new data
    data_time.append(current_time)
    data_x.append(quat[0])
    data_y.append(quat[1])
    data_z.append(quat[2])
    data_w.append(quat[3])

    data_time_list = list(data_time)

    # Update the plot series values. Each series is a two-element list: [list_of_x, list_of_y]
    dpg.set_value("series_x", [data_time_list, list(data_x)])
    dpg.set_value("series_y", [data_time_list, list(data_y)])
    dpg.set_value("series_z", [data_time_list, list(data_z)])
    dpg.set_value("series_w", [data_time_list, list(data_w)])
    dpg.set_axis_limits(tag, data_time[0], data_time[-1])


# --- Dear PyGui Setup ---
dpg.create_context()

with dpg.window(label="Quaternion Plot", tag="Prim"):
    with dpg.plot(label="Quaternion Components Over Time", width=-1, height=-1):
        tag = dpg.add_plot_axis(dpg.mvXAxis, label="Time")
        with dpg.plot_axis(dpg.mvYAxis, label="Component Value"):
            dpg.add_line_series([], [], label="X", tag="series_x")
            dpg.add_line_series([], [], label="Y", tag="series_y")
            dpg.add_line_series([], [], label="Z", tag="series_z")
            dpg.add_line_series([], [], label="W", tag="series_w")


dpg.create_viewport(title="Dear PyGui: Quaternion Plot", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Prim", True)


async def main() -> None:
    """
    An example showing using API related to discovering nodes existing
    on control and telemetry lines.
    """
    async with Client(address="/run/clone", tunnels_used=Client.TunnelsUsed.STATE) as client:

        async for tele in client.subscribe_telemetry():
            imus = tele.imu
            r_imus = {imu.node_id: R.from_quat([imu.x, imu.y, imu.z, imu.w]) for imu in imus}
            imus_id = sorted(r_imus.keys(), reverse=True)
            r_rels = {
                f"{id_parent}-{id_child}": r_imus[id_parent].inv() * r_imus[id_child]
                for id_parent, id_child in pairwise(imus_id)
            }

            print("\n" * 20)
            for descr, r in r_rels.items():
                print(f"{descr}: {r.as_quat()}")

            update_data(r_rels[key].as_quat())
            dpg.render_dearpygui_frame()


asyncio.run(main())
dpg.destroy_context()
