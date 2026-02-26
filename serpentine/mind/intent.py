from typing import Optional, Dict, Any
try:
    from pydantic import BaseModel, Field
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, Field

class Intent(BaseModel):
    """
    Base class for all intents.
    Represents a desired action from the cognitive system.
    """
    type: str
    target: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class ClickIntent(Intent):
    """Simulates a mouse click."""
    type: str = "click"
    x: int
    y: int
    button: str = "left"

class MoveIntent(Intent):
    """Simulates mouse movement."""
    type: str = "move"
    x: int
    y: int
    duration: float = 0.0

class KeyIntent(Intent):
    """Simulates keyboard input."""
    type: str = "key"
    key: str
    action: str = "press"  # press, down, up

class ChangeDirectionIntent(Intent):
    """
    Intent to change the movement direction of an entity (e.g. Snake).
    """
    type: str = "change_direction"
    direction: str  # UP, DOWN, LEFT, RIGHT
