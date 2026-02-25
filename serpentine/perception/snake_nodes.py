from typing import Optional, Any
import logging
try:
    import numpy as np
except ImportError:
    np = None

from serpentine.perception.nodes import PerceptionNode
from serpentine.perception.types import Observation

logger = logging.getLogger(__name__)

class InternalGridPerceptionNode(PerceptionNode):
    """
    Converts snake game state into a 2D grid observation.
    Grid values: 0=Empty, 1=Snake Body, 2=Snake Head, 3=Food
    """
    def __init__(self, name: str = "internal_grid"):
        super().__init__(name)
        if np is None:
            logger.warning(f"Numpy not available. {self.name} will use list of lists.")

    def process(self, input_data: Observation, **kwargs) -> Optional[Observation]:
        if input_data.data_type != "game_state":
            return None

        state = input_data.content
        w = state.get("board_width", 10)
        h = state.get("board_height", 10)
        segments = state.get("snake_segments", [])
        food_pos = state.get("food_position", (0, 0))

        if np:
            grid = np.zeros((h, w), dtype=np.uint8)
            # Draw food
            fx, fy = food_pos
            if 0 <= fx < w and 0 <= fy < h:
                grid[fy, fx] = 3
            # Draw snake
            for i, (sx, sy) in enumerate(segments):
                if 0 <= sx < w and 0 <= sy < h:
                    if i == 0:
                        grid[sy, sx] = 2 # Head
                    else:
                        grid[sy, sx] = 1 # Body
        else:
            grid = [[0 for _ in range(w)] for _ in range(h)]
            # Draw food
            fx, fy = food_pos
            if 0 <= fx < w and 0 <= fy < h:
                grid[fy][fx] = 3
            # Draw snake
            for i, (sx, sy) in enumerate(segments):
                if 0 <= sx < w and 0 <= sy < h:
                    if i == 0:
                        grid[sy][sx] = 2 # Head
                    else:
                        grid[sy][sx] = 1 # Body

        return Observation(
            source_node=self.name,
            data_type="grid_map",
            content=grid,
            metadata={
                "grid_size": (w, h),
                "mapping": {"empty": 0, "body": 1, "head": 2, "food": 3}
            }
        )
