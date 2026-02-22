from core.system import System
from core.world import World
from components.core import ActionBufferComponent

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

            # Peek at the current action
            current_action = buffer.queue[0]

            # In a real implementation, we would check if action is already running
            # if buffer.current_action_status == "RUNNING": ...

            # Execute
            try:
                # Assuming BaseAction has an async execute method
                status = await current_action.execute()
                # If SUCCESS or FAILURE, remove from queue
                if status in ["SUCCESS", "FAILURE"]:
                    buffer.queue.pop(0)
                    buffer.current_action_status = status
                elif status == "RUNNING":
                    buffer.current_action_status = "RUNNING"
            except Exception as e:
                print(f"Action execution failed: {e}")
                buffer.queue.pop(0)
                buffer.current_action_status = "FAILURE"
