from pydantic import Field
from typing import Literal
from actions.base import BaseAction

try:
    import pyautogui
except ImportError:
    pyautogui = None

class ClickAction(BaseAction):
    """Action to perform a mouse click at specific coordinates."""
    target_env: Literal["EXTERNAL_OS", "INTERNAL_ENGINE"] = "EXTERNAL_OS"
    x: int = Field(description="X coordinate of the screen")
    y: int = Field(description="Y coordinate of the screen")
    button: Literal["left", "right", "middle"] = "left"

    async def execute(self):
        if pyautogui is None:
            print("pyautogui is not installed. Mocking ClickAction.")
            return "SUCCESS"
        
        try:
            pyautogui.click(x=self.x, y=self.y, button=self.button)
            return "SUCCESS"
        except Exception as e:
            print(f"ClickAction failed: {e}")
            return "FAILURE"

class MoveAction(BaseAction):
    """Action to move the mouse cursor to specific coordinates."""
    target_env: Literal["EXTERNAL_OS", "INTERNAL_ENGINE"] = "EXTERNAL_OS"
    x: int = Field(description="X coordinate of the screen")
    y: int = Field(description="Y coordinate of the screen")
    duration: float = Field(default=0.2, description="Duration of the mouse movement in seconds")

    async def execute(self):
        if pyautogui is None:
            print("pyautogui is not installed. Mocking MoveAction.")
            return "SUCCESS"
        
        try:
            pyautogui.moveTo(x=self.x, y=self.y, duration=self.duration)
            return "SUCCESS"
        except Exception as e:
            print(f"MoveAction failed: {e}")
            return "FAILURE"
