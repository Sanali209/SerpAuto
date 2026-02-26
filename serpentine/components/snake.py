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
    Component representing the snake's body.
    Segments are stored as a list of (x, y) coordinates on the grid.
    The first element is the head, the last is the tail.
    """
    segments: List[Tuple[int, int]] = Field(default_factory=list)
    current_direction: str = "UP"  # UP, DOWN, LEFT, RIGHT
    next_direction: str = "UP"     # To prevent 180-degree turns in one tick
    last_tail_pos: Tuple[int, int] = (0, 0) # Used for growing the snake

@Registry.register_component
class SnakeFoodComponent(BaseComponent):
    """
    Component representing food for the snake.
    """
    value: int = 1  # Score value / growth amount

@Registry.register_component
class SnakeConfigComponent(BaseComponent):
    """
    Configuration for the Snake game.
    Usually attached to a global or level entity.
    """
    grid_width: int = 20
    grid_height: int = 20
    cell_size: int = 20  # For rendering/visualization
    move_interval: float = 0.1  # Seconds between moves (if using time-based movement)
    last_move_time: float = 0.0
