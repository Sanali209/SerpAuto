from typing import Literal
from actions.base import BaseAction
from components.internal import VelocityComponent

class ChangeDirectionAction(BaseAction):
    direction: Literal["UP", "DOWN", "LEFT", "RIGHT"]
    target_env: Literal["EXTERNAL_OS", "INTERNAL_ENGINE"] = "INTERNAL_ENGINE"

    async def execute(self, world=None, entity_id=None):
        # NOTE: The base execute() signature might need to change to accept world context
        # for Internal actions. In `systems/action.py`, we call execute().
        # Standard Command pattern usually encapsulates the receiver, but here the receiver is dynamic (the entity).
        # We'll assume the system handles the logic or passes context.
        # For this sample, let's assume `execute` is called with context injection if needed,
        # OR the system handles specific action types directly (like described in the design doc).

        # Design Doc says: "ActionExecutionSystem sees this action... and changes VelocityComponent"
        # So logic likely resides in the System for Internal actions, or the Action modifies the component directly if passed.
        pass
