from typing import List, Dict, Type, Optional
import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.core.world import World

class WindowManager:
    """
    Manages the lifecycle and updates of all GUI windows.
    """
    def __init__(self):
        self.windows: Dict[str, BaseUIWindow] = {}

    def register_window(self, window: BaseUIWindow):
        """
        Registers a window instance.
        """
        if window.window_tag not in self.windows:
            self.windows[window.window_tag] = window
            window.setup()

    def update(self, world: World, dt: float):
        """
        Updates all active windows.
        """
        for window in self.windows.values():
            if window.show:
                if dpg.is_item_shown(window.window_tag):
                    window.update(world, dt)

    def get_window(self, tag: str) -> Optional[BaseUIWindow]:
        return self.windows.get(tag)

    def toggle_window(self, tag: str):
        """
        Toggles the visibility of a window.
        """
        window = self.get_window(tag)
        if window:
            window.show = not window.show
            if window.show:
                dpg.show_item(window.window_tag)
            else:
                dpg.hide_item(window.window_tag)
