import numpy as np
from perception.nodes import PerceptionNode
from components.snake import GridPositionComponent, SnakeBodyComponent, SnakeColliderComponent

class InternalGridStateNode(PerceptionNode):
    """
    Constructs a 1D observation vector from the internal ECS grid state.
    Used for RL agents bypassing CV pipelines.
    """
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height

    def process(self, context: dict) -> dict:
        # We need the world here, but perception nodes usually work on 'context'.
        # For InternalState, we assume the system passes the world or raw entities info.
        # However, the design doc says nodes are part of the pipeline.
        # I'll update the pipeline to pass the world if needed, or extract data beforehand.
        
        world = context.get("_world")
        if not world:
            return context

        # Grid: 0: Empty, 1: Snake Head, 2: Snake Body, 3: Apple
        grid = np.zeros((self.height, self.width), dtype=np.float32)

        # 1. Fill Apples
        apples = world.get_entities_with(SnakeColliderComponent, GridPositionComponent)
        for ent in apples:
            collider = world.get_component(ent, SnakeColliderComponent)
            pos = world.get_component(ent, GridPositionComponent)
            if collider.type == "apple" and 0 <= pos.x < self.width and 0 <= pos.y < self.height:
                grid[pos.y, pos.x] = 3.0

        # 2. Fill Snake
        snakes = world.get_entities_with(SnakeBodyComponent, GridPositionComponent)
        for ent in snakes:
            pos = world.get_component(ent, GridPositionComponent)
            body = world.get_component(ent, SnakeBodyComponent)
            
            # Body
            for bx, by in body.body_segments:
                if 0 <= bx < self.width and 0 <= by < self.height:
                    grid[by, bx] = 2.0
            
            # Head
            if 0 <= pos.x < self.width and 0 <= pos.y < self.height:
                grid[pos.y, pos.x] = 1.0

        context["grid_observation"] = grid.flatten().tolist()
        return context
