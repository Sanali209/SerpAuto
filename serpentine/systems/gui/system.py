import dearpygui.dearpygui as dpg
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.systems.gui.manager import WindowManager
from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.core.registry_v2 import RegistryV2

# Ensure windows are registered by importing them
from serpentine.systems.gui.windows.control_deck import ControlDeck
from serpentine.systems.gui.windows.outliner import Outliner
from serpentine.systems.gui.windows.inspector import Inspector
from serpentine.systems.gui.windows.viewport import Viewport
from serpentine.systems.gui.graph.bt_editor import BehaviorTreeEditor
from serpentine.systems.gui.graph.perception_editor import PerceptionGraphEditor

@Registry.register_system(phase=SystemPhase.TELEMETRY, modes=[EngineMode.ARCHITECT, EngineMode.TEACHER])
class GUIDebugSystem(System):
    """
    Main system for the Developer UI (God Mode).
    Orchestrates the DPG context and manages windows.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate)
        self.window_manager = WindowManager()
        self.dpg_context_created = False
        self.is_running = False

    def setup_dpg(self):
        """Initializes DearPyGui context."""
        if self.dpg_context_created:
            return

        dpg.create_context()
        dpg.create_viewport(title="Serpentine Engine - God Mode", width=1600, height=900)
        dpg.setup_dearpygui()

        # Enable docking
        dpg.configure_app(docking=True, docking_space=True)

        # Register windows via RegistryV2 discovery
        for window_cls in RegistryV2.get_all_windows():
            # Instantiate the window
            # Assuming all windows have no-arg constructors
            window_instance = window_cls()
            self.window_manager.register_window(window_instance)

        dpg.show_viewport()
        self.dpg_context_created = True

    async def update(self, world: World, dt: float) -> None:
        """
        Updates the GUI.
        """
        if not self.dpg_context_created:
            self.setup_dpg()

        if dpg.is_dearpygui_running():
            # Update windows
            self.window_manager.update(world, dt)

            # Render frame
            dpg.render_dearpygui_frame()
        else:
            # If DPG window is closed
            pass

    def shutdown(self):
        if self.dpg_context_created:
            dpg.destroy_context()
