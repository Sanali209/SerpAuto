from typing import Optional
try:
    import dearpygui.dearpygui as dpg
except ImportError:
    dpg = None

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.components.simulation import InputControlComponent
from serpentine.perception.components import ActionBufferComponent
from serpentine.mind.intent import KeyIntent

@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.TEACHER, EngineMode.ARCHITECT])
class HumanInputSystem(System):
    """
    Captures human input (Keyboard/Mouse) via DearPyGui and converts it to Intents.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)
        self.key_map = {}
        if dpg:
            self.key_map = {
                dpg.mvKey_W: "Up",
                dpg.mvKey_S: "Down",
                dpg.mvKey_A: "Left",
                dpg.mvKey_D: "Right",
                dpg.mvKey_Up: "Up",
                dpg.mvKey_Down: "Down",
                dpg.mvKey_Left: "Left",
                dpg.mvKey_Right: "Right",
            }

    async def update(self, world: World, dt: float) -> None:
        if not dpg or not dpg.is_dearpygui_running():
            return

        # Find controllable entities
        # We need entities that have InputControlComponent AND ActionBufferComponent
        # Using intersection for efficiency

        # This is slightly inefficient if we don't have a direct query, but get_entities_with handles it.
        entities = world.get_entities_with(InputControlComponent, ActionBufferComponent)

        active_key = None
        # Check keys
        # We prioritize one key press per tick for simple games like Snake
        for key_code, action_name in self.key_map.items():
            if dpg.is_key_down(key_code):
                active_key = action_name
                break # Prioritize first found key

        if active_key:
            intent = KeyIntent(key=active_key, action="press")
            for entity_id, input_comp, action_buffer in entities:
                if input_comp.enabled:
                    # Enqueue intent
                    # Optionally clear previous if only one per frame desired?
                    # For Snake, we might want to just append.
                    action_buffer.enqueue(intent)
