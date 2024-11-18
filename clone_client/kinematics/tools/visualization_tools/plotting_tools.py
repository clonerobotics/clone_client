"""IMU relative angles assessment tool."""

from abc import ABC, abstractmethod
from collections import deque
import logging
from typing import Annotated, Any, Callable, Optional, Sequence

import dearpygui.dearpygui as dpg
import numpy as np
from scipy.spatial.transform import Rotation

from clone_client.kinematics.tools.visualization_tools.dpg_app import MainApp

L = logging.getLogger(__name__)


class Plot:
    def __init__(
        self,
        parent: str | int,
        label: str,
        xlabel: str,
        ylabel: str,
        y_axis_limits: tuple[float, float] = (-1.0, 1.0),
    ) -> None:
        with dpg.plot(label=label, parent=parent) as plot:
            self._plot_tag = plot
            dpg.add_plot_legend()
            self._axis_x = dpg.add_plot_axis(dpg.mvXAxis, label=xlabel)
            self._axis_y = dpg.add_plot_axis(dpg.mvYAxis, label=ylabel)
            self._series: dict[int | str, tuple[deque[float], deque[float]]] = {}
            dpg.set_axis_limits(self._axis_y, y_axis_limits[0], y_axis_limits[1])

    def add_series(
        self,
        x: Optional[Sequence[float]] = None,
        y: Optional[Sequence[float]] = None,
        label: Optional[str] = None,
    ) -> int:
        """Returns a tag used to select series to update"""
        if x is None:
            x = tuple()
        if y is None:
            y = tuple()
        if label is None:
            label = ""
        series_tag = dpg.add_line_series(tuple(x), tuple(y), label=label, parent=self._axis_y)
        if not isinstance(series_tag, int):
            raise TypeError()
        self._series[series_tag] = (deque(maxlen=1000), deque(maxlen=1000))
        return series_tag

    def update_series(self, series_tag: int | str, new_x: float, new_y: float):
        x, y = self._series[series_tag]
        x.append(new_x)
        y.append(new_y)
        dpg.set_value(series_tag, [tuple(x), tuple(y)])
        dpg.set_axis_limits(self._axis_x, x[0], x[-1])

    def update_plot(self, new_x: float, new_y: Any):
        _ = new_y
        _ = new_x
        raise NotImplementedError("Not implemented for a generic plot")


class PlotRot(Plot, ABC):
    @abstractmethod
    def update_plot(self, new_x: float, new_y: Rotation): ...


class PlotQuat(PlotRot):
    def __init__(
        self,
        parent: str | int,
        label: str,
        xlabel: str = "time[s]",
        ylabel: str = "normalized length",
        y_axis_limits: tuple[float, float] = (-1, 1),
    ) -> None:
        super().__init__(parent, label, xlabel, ylabel, y_axis_limits)
        self._oredered_tags = [
            self.add_series(label="w"),
            self.add_series(label="x"),
            self.add_series(label="y"),
            self.add_series(label="z"),
        ]

    def update_plot(self, new_x: float, new_y: Rotation):
        rot_quat = new_y.as_quat(scalar_first=True)
        for idx, tag in enumerate(self._oredered_tags):
            self.update_series(tag, new_x, rot_quat[idx])


class PlotAxisAngle(PlotRot):
    def __init__(
        self,
        parent: str | int,
        label: str,
        xlabel: str = "time[s]",
        ylabel: str = "normalized length",
        y_axis_limits: tuple[float, float] = (-1.1, 1.1),
        ylabel_angle: str = "angle[deg]",
        y_axis_limits_angle: tuple[float, float] = (0.0, 100.0),
    ) -> None:
        super().__init__(parent, label, xlabel, ylabel, y_axis_limits)
        self._axis_y_angle = dpg.add_plot_axis(dpg.mvYAxis, label=ylabel_angle, parent=self._plot_tag)
        self._xser = self.add_series(label="x")
        self._yser = self.add_series(label="y")
        self._zser = self.add_series(label="z")
        self._angleser = dpg.add_line_series(tuple(), tuple(), label="angle", parent=self._axis_y_angle)
        dpg.set_axis_limits(self._axis_y_angle, y_axis_limits_angle[0], y_axis_limits_angle[1])
        self._series[self._angleser] = (deque(maxlen=1000), deque(maxlen=1000))

    def update_plot(self, new_x: float, new_y: Rotation):
        rotvec = new_y.as_rotvec(degrees=False)
        # extract angle and normalize vector
        angle = new_y.magnitude()
        rotvec = rotvec / angle
        self.update_series(self._xser, new_x, rotvec[0])
        self.update_series(self._yser, new_x, rotvec[1])
        self.update_series(self._zser, new_x, rotvec[2])
        self.update_series(self._angleser, new_x, np.rad2deg(angle))  # type: ignore


class PlotEuler(PlotRot):
    def __init__(
        self,
        parent: str | int,
        label: str,
        xlabel: str = "time[s]",
        ylabel: str = "angle [deg]",
        y_axis_limits: tuple[float, float] = (-180.0, 180.0),
    ) -> None:
        super().__init__(parent, label, xlabel, ylabel, y_axis_limits)
        self._oredered_tags = [
            self.add_series(label="x"),
            self.add_series(label="y"),
            self.add_series(label="z"),
        ]

    def update_plot(self, new_x: float, new_y: Rotation):
        rot_eul = new_y.as_euler("xyz", degrees=True)
        for idx, tag in enumerate(self._oredered_tags):
            self.update_series(tag, new_x, rot_eul[idx])


class PlottingWindow:
    def __init__(self, widg_creating_func=dpg.add_window) -> None:
        self._plot_list: list[Plot] = []
        self._self_tag = widg_creating_func()
        self._subplots = dpg.add_subplots(0, 1, label="Plots", width=-1, height=-1, parent=self._self_tag)
        self._plots_number = 0

    def add_plot(self, plot_type: type[Plot] = Plot, **kwargs) -> Plot:
        """Add generic plot"""
        self._plots_number += 1
        dpg.configure_item(self._subplots, rows=self._plots_number)
        plot = plot_type(self._subplots, **kwargs)
        self._plot_list.append(plot)
        return plot


class RotationsPlottingWindow(PlottingWindow):

    def add_plot_quat(self, label: str = "") -> PlotRot:
        """Does not have to be in physical, in-chain, order. Should be call before 'main'
        Generates plot of relative quaternion.
        """
        return self.add_plot(label=label, plot_type=PlotQuat, xlabel="time[s]", ylabel="quat length")

    def add_plot_axisangle(self, label: str = "", y_axis_limits_angle=(0.0, 360.0)) -> PlotRot:
        return self.add_plot(
            label=label,
            plot_type=PlotAxisAngle,
            xlabel="time[s]",
            ylabel="vec length",
            y_axis_limits_angle=y_axis_limits_angle,
        )

    def add_plot_euler(self, label: str = "", y_axis_limits=(-180.0, 180.0)) -> PlotRot:
        return self.add_plot(
            label=label,
            plot_type=PlotEuler,
            xlabel="time[s]",
            ylabel="angle [deg]",
            y_axis_limits=y_axis_limits,
        )


class RotationPlottingMainApp(MainApp, RotationsPlottingWindow):
    """Convinience class for creating DPG app with PlottingWindow.
    GUI task is delegated to its own thread.
    """

    def __init__(self, end_hook: Callable | None = None) -> None:
        MainApp.__init__(self, "Relative rotations previewer", end_hook)
        RotationsPlottingWindow.__init__(self)

    def _gui_thread_task(self):
        dpg.set_primary_window(self._self_tag, True)
        super()._gui_thread_task()


def main():
    L.info("Starting IMU relative assessment tool.")
    relative_plots_dict: dict[tuple[Annotated[int, "parent_id"], Annotated[int, "child_id"]], Plot] = {}
    app = RotationPlottingMainApp()
    relative_plots_dict[0x42, 0x40] = app.add_plot_quat(
        "Relative rotation between parent 0x42 and child 0x40 - quat"
    )
    relative_plots_dict[0x42, 0x40] = app.add_plot_axisangle(
        "Relative rotation between parent 0x42 and child 0x40 - axis-angle"
    )
    relative_plots_dict[0x42, 0x40] = app.add_plot_axisangle("Jointal coordinates - axis-angle")
    app.start()
    input()
    L.info("Bye")


if __name__ == "__main__":
    main()
