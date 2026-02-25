from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
import dearpygui.dearpygui as dpg
from serpentine.core.world import World
from serpentine.core.event_bus import GUIEventBus

class BaseUIWindow(ABC):
    """
    Abstract base class for all GUI windows.
    """
    def __init__(self, window_tag: str, label: str, width: int = 400, height: int = 300, show: bool = True):
        self.window_tag = window_tag
        self.label = label
        self.width = width
        self.height = height
        self.show = show
        self.initialized = False

    def setup(self):
        """
        Creates the DPG window and calls render().
        Should be called once during initialization.
        """
        if not self.initialized:
            with dpg.window(tag=self.window_tag, label=self.label, width=self.width, height=self.height, show=self.show):
                self.render()
            self.initialized = True

    @abstractmethod
    def render(self):
        """
        Defines the static structure of the window.
        Called inside the dpg.window context.
        """
        pass

    @abstractmethod
    def update(self, world: World, dt: float):
        """
        Updates the window content based on the current world state.
        Called every frame.
        """
        pass
