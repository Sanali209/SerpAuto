from typing import List, Tuple
try:
    from pydantic import Field
except ImportError:
    from serpentine.utils.pydantic_utils import Field

from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry

@Registry.register_component
class SnakeBodyComponent(BaseComponent):
    """
    Represents the snake's body as a list of coordinates.
    segments[0] is the head.
    """
    segments: List[Tuple[int, int]] = Field(default_factory=list)
    direction: Tuple[int, int] = (1, 0)  # (dx, dy), initially moving right
    grow_pending: int = 0
    is_dead: bool = False

@Registry.register_component
class SnakeFoodComponent(BaseComponent):
    """
    Tags an entity as food.
    """
    position: Tuple[int, int] = (0, 0)

@Registry.register_component
class SnakeConfigComponent(BaseComponent):
    """
    Configuration for the Snake game.
    """
    board_width: int = 10
    board_height: int = 10
    max_steps: int = 1000
    current_step: int = 0
