import logging
from typing import Any, Callable, Optional

import numpy as np
import roboticstoolbox as rtb
from roboticstoolbox.robot.BaseRobot import PyPlot

L = logging.getLogger(__name__)


class KinematicsVisualizer:
    def __init__(self, ets: rtb.ETS, on_close: Optional[Callable[[Any], None]] = None) -> None:

        self._dofs: int = len(ets.joints())
        self._robot: rtb.Robot = rtb.Robot(ets)
        self._robot.q = np.zeros((self._dofs,), dtype=np.float64)
        self._plot = self._robot.plot(self._robot.q, block=False, limits=[-1.0, 1.0, -1.0, 1.0, -1.0, 1.0])
        if not isinstance(self._plot, PyPlot):
            raise RuntimeError("Wrong type of plot obtained")
        if on_close is not None:
            self._plot.fig.canvas.mpl_connect("close_event", on_close)

        L.info("KinematicsVisualizer initialized")

    def update_plot(self, q: list[float]):
        L.debug("New q: %s", q)
        self._robot.q = q
        self._plot.step()
