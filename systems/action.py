import logging
from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import ActionBufferComponent
from components.internal import VelocityComponent

logger = logging.getLogger(__name__)

# Import custom actions
try:
    from actions.snake import ChangeDirectionAction
except ImportError:
    ChangeDirectionAction = None

@register_system(phase=Phase.EXECUTION)
class ActionExecutionSystem(System):
    """
    Processes the ActionBufferComponent and executes actions sequentially.
    """
    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(ActionBufferComponent)
        for entity in entities:
            buffer = world.get_component(entity, ActionBufferComponent)
            if not buffer.queue:
                continue

            current_action = buffer.queue[0]
            status = "FAILURE"

            try:
                # Get BrainComponent for I/O status management
                from components.core import BrainComponent
                brain = world.get_component(entity, BrainComponent)

                # Handle Specific Actions (Command Pattern dispatch)
                if ChangeDirectionAction and isinstance(current_action, ChangeDirectionAction):
                    status = self._handle_snake_move(world, entity, current_action)
                else:
                    # Default handling
                    status = await current_action.execute()

                # Update Queue
                if status in ["SUCCESS", "FAILURE"]:
                    buffer.queue.pop(0)
                    buffer.current_action_status = status
                    
                    # If brain exists and this was an external action, wait for next frame
                    if brain and getattr(current_action, "target_env", "") == "EXTERNAL_OS":
                        brain.status = "WAITING_FOR_IO"
                        logger.debug(f"Entity {entity} brain locked WAITING_FOR_IO after OS action.")

                elif status == "RUNNING":
                    buffer.current_action_status = "RUNNING"

            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                buffer.queue.pop(0)
                buffer.current_action_status = "FAILURE"

    def _handle_snake_move(self, world: World, entity: int, action) -> str:
        """Handler for ChangeDirectionAction in Snake sample."""
        vel = world.get_component(entity, VelocityComponent)
        if not vel:
            return "FAILURE"

        if action.direction == "UP":
            vel.vx, vel.vy = 0, -1
        elif action.direction == "DOWN":
            vel.vx, vel.vy = 0, 1
        elif action.direction == "LEFT":
            vel.vx, vel.vy = -1, 0
        elif action.direction == "RIGHT":
            vel.vx, vel.vy = 1, 0

        return "SUCCESS"
