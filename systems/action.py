from core.system import System
from core.world import World
from components.core import ActionBufferComponent
from components.internal import VelocityComponent

# Import custom actions
try:
    from actions.snake import ChangeDirectionAction
except ImportError:
    ChangeDirectionAction = None

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
                elif status == "RUNNING":
                    buffer.current_action_status = "RUNNING"

            except Exception as e:
                print(f"Action execution failed: {e}")
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
