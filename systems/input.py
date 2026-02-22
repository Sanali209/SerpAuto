from core.system import System
from core.world import World
from components.core import ActionBufferComponent

class HumanInputSystem(System):
    """
    Captures user input from GUI (Mouse/Keyboard) and pushes Actions to Buffer.
    Active in TEACHER mode.
    """
    async def update(self, world: World, dt: float):
        # Placeholder: Check dpg.get_mouse_pos()
        pass
