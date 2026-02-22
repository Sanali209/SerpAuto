from typing import Dict, Any, List
from core.component import BaseComponent
from core.world import World
from components.snake import GridPositionComponent, SnakeBodyComponent, SnakeColliderComponent

class InternalGridStateNode:
    """
    Scans ECS World and builds a 2D matrix for the Snake Agent.
    0=Empty, 1=Body, 2=Head, 3=Apple
    """
    def process(self, world: World) -> Dict[str, Any]:
        grid = [[0 for _ in range(10)] for _ in range(10)]

        # 1. Fill Apple
        apples = world.get_entities_with(SnakeColliderComponent, GridPositionComponent)
        for ent in apples:
            collider = world.get_component(ent, SnakeColliderComponent)
            if collider.type == "apple":
                pos = world.get_component(ent, GridPositionComponent)
                if 0 <= pos.x < 10 and 0 <= pos.y < 10:
                    grid[pos.y][pos.x] = 3

        # 2. Fill Snake
        snakes = world.get_entities_with(SnakeBodyComponent, GridPositionComponent)
        for ent in snakes:
            # Body
            body = world.get_component(ent, SnakeBodyComponent)
            for (bx, by) in body.body_segments:
                if 0 <= bx < 10 and 0 <= by < 10:
                    grid[by][bx] = 1

            # Head
            head_pos = world.get_component(ent, GridPositionComponent)
            if 0 <= head_pos.x < 10 and 0 <= head_pos.y < 10:
                grid[head_pos.y][head_pos.x] = 2

        return {"grid": grid}
