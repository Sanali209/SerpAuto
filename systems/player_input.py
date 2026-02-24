import glfw
from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import PlayerControllerComponent, ActionBufferComponent

@register_system(phase=Phase.INPUT)
class PlayerInputSystem(System):
    """
    Captures human input from GLFW and routes it to the player's ActionBuffer.
    """
    def __init__(self):
        self.window = None

    async def update(self, world: World, dt: float):
        # We need to find the window from the Render system or engine
        # For a stub, we assume the last active current context
        self.window = glfw.get_current_context()
        if not self.window:
            return

        players = world.get_entities_with(PlayerControllerComponent, ActionBufferComponent)
        for entity in players:
            buffer = world.get_component(entity, ActionBufferComponent)
            
            # Simple WASD mapping
            if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
                # buffer.queue.append(MoveAction(direction="UP"))
                pass
            if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
                pass
            # ... and so on
