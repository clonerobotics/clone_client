from threading import Thread
from typing import Callable

import dearpygui.dearpygui as dpg


class MainApp:
    """Convinience class for creating DPG app.
    GUI task is delegated to its own thread.
    """

    def __init__(self, viewport_title: str = "MainApp", end_hook: Callable | None = None) -> None:
        dpg.create_context()
        self._t = Thread(target=self._gui_thread_task, daemon=True)
        self._end_hook: Callable | None = end_hook
        dpg.create_viewport(title=viewport_title)
        dpg.setup_dearpygui()

    def start(self):
        self._t.start()

    @property
    def end_event(self) -> Callable | None:
        """GUI end event."""
        return self._end_hook

    def _gui_thread_task(self):
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        if self._end_hook is not None:
            self._end_hook()
