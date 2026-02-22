from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import ActionBufferComponent

@register_system(phase=Phase.PERCEPTION)
class HumanInputSystem(System):
    """
    Captures user input from GUI (Mouse/Keyboard) and pushes Actions to Buffer.
    Active in TEACHER mode.
    """
    async def update(self, world: World, dt: float):
        # Placeholder: Check dpg.get_mouse_pos()
        pass
