from typing import Literal
from pydantic import BaseModel, Field

class BaseAction(BaseModel):
    """Base class for all actions (Click, Type, Move, etc.)"""
    target_env: Literal["EXTERNAL_OS", "INTERNAL_ENGINE"] = "EXTERNAL_OS"

    async def execute(self):
        """Execute the action in the target environment"""
        # Placeholder
        print(f"Executing action in {self.target_env}")
        return "SUCCESS"
