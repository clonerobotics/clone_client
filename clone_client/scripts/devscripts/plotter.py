import asyncio
from collections import deque
from os import environ
from pathlib import Path
from time import time

import dearpygui.dearpygui as dpg
import numpy as np

from clone_client.client import Client
from clone_client.magnet import CalibrationDataRaw, gauss_rider_rewrap, GaussCalculator

SENSOR_IDS = [0x7D, 0x82, 0x92]
PIXEL_COUNT = 4
AXES_COUNT = 3


def create_plots():
    dpg.create_context()
    dpg.create_viewport(title="GaussRider data viewer", width=900, height=700)

    with dpg.window(tag="GaussRider data viewer", width=1200, height=680):
        with dpg.group(horizontal=False):
            for sensor_id in SENSOR_IDS:
                with dpg.group(horizontal=True):
                    dpg.add_text(f"{sensor_id}")
                    for i in range(PIXEL_COUNT):
                        with dpg.plot(label=f"Pixel {i}", height=500, width=475):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(
                                dpg.mvXAxis, label="X Axis", tag=f"node.{sensor_id}_pixel.{i}_xaxis"
                            )
                            y_axis = dpg.add_plot_axis(
                                dpg.mvYAxis, label="Y Axis", tag=f"node.{sensor_id}_pixel.{i}_yaxis"
                            )
                            for s in "xyz":
                                tag = f"node.{sensor_id}_pixel.{i}_axis.{s}"
                                dpg.add_line_series([], [], label=f"Series {s}", parent=y_axis, tag=tag)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("GaussRider data viewer", True)


def update_plots(data: dict):
    for plot_key, series_dict in data.items():
        for series_key, (x_vals, y_vals) in series_dict.items():
            tag = f"{plot_key}_{series_key}"
            dpg.set_value(tag, [list(x_vals), list(y_vals)])
        dpg.fit_axis_data(f"{plot_key}_xaxis")
        dpg.fit_axis_data(f"{plot_key}_yaxis")
    if not dpg.is_dearpygui_running():
        raise KeyboardInterrupt()


def load_calibration_data(dir_name: str) -> dict[int, CalibrationDataRaw]:
    path = Path(dir_name)
    calibs = {}
    for file in path.iterdir():
        print("found file: ", file.name)
        constant, node_id, suffix = file.name.split(".")
        if constant != "gauss_rider_raw_calib" or suffix != "json":
            raise RuntimeError("Invalid name")
        calibs[int(node_id)] = CalibrationDataRaw.load(str(file))
    return calibs


async def main():
    print("main started")
    dpg.render_dearpygui_frame()
    start_time = time()
    address = environ.get("GOLEM_ADDRESS", "127.0.0.1")
    calib_dir = environ.get("CALIB_DIR") or "./fetched_calibration"
    convert = environ.get("CONVERT")
    match convert:
        case "local" | "LOCAL":
            calib_data = load_calibration_data(calib_dir)
            calibs = {node_id: GaussCalculator(calib) for node_id, calib in calib_data.items()}
        case None:
            calibs = None
        case _:
            calibs = True

    async with Client(address=address, tunnels_used=Client.TunnelsUsed.STATE) as client:
        print("client connected")
        data = {
            f"node.{sensor_id}_pixel.{px}": {
                f"axis.{ax}": (deque(maxlen=2000), deque(maxlen=2000)) for ax in "xyz"
            }
            for sensor_id in SENSOR_IDS
            for px in range(4)
        }
        last_render_time = -float("inf")
        async for tele in client.subscribe_telemetry():
            try:
                curr_time = time()
                time_since_start = curr_time - start_time
                grs = {gr.node_id: gr for gr in tele.sensor_data.gauss_rider_data}
                for sensor_id in SENSOR_IDS:
                    s = grs[sensor_id]
                    if calibs is True:
                        bfield = np.array(tele.sensor_data.bfields[sensor_id].bfield).reshape(4, 3) * 1000.0
                        for px_nr, px in enumerate(bfield):
                            for ax_nr, ax in enumerate("xyz"):
                                t, x = data[f"node.{sensor_id}_pixel.{px_nr}"][f"axis.{ax}"]
                                t.append(time_since_start)
                                x.append(px[ax_nr])
                    elif calibs is not None:
                        out = (
                            calibs[sensor_id].calculate_bfield([gauss_rider_rewrap(grs[sensor_id])]) * 1000.0
                        )
                        for px_nr, px in enumerate(out[0]):
                            for ax_nr, ax in enumerate("xyz"):
                                t, x = data[f"node.{sensor_id}_pixel.{px_nr}"][f"axis.{ax}"]
                                t.append(time_since_start)
                                x.append(px[ax_nr])
                    else:
                        for px_nr, px in enumerate(s.sensor.pixels):
                            for ax in "xyz":
                                t, x = data[f"node.{sensor_id}_pixel.{px_nr}"][f"axis.{ax}"]
                                t.append(time_since_start)
                                x.append(getattr(px, ax))
                update_plots(data)
                if curr_time - last_render_time > 0.1:
                    last_render_time = curr_time
                    dpg.render_dearpygui_frame()
            except KeyError:
                continue


if __name__ == "__main__":
    create_plots()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    dpg.destroy_context()
