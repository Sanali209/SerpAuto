import random
import logging
from typing import Tuple, List, Optional, Dict, Any

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.components.snake import SnakeBodyComponent, SnakeFoodComponent, SnakeConfigComponent
from serpentine.perception.components import ActionBufferComponent, PerceptionComponent
from serpentine.perception.types import Observation
from serpentine.mind.intent import Intent
from serpentine.components.simulation import RewardComponent

logger = logging.getLogger(__name__)

class SnakeDirectionIntent(Intent):
    type: str = "snake_direction"
    direction: Tuple[int, int] # (dx, dy)

@Registry.register_system(phase=SystemPhase.EXECUTION, modes=[EngineMode.GYMNASIUM, EngineMode.PRODUCTION])
class SnakeActionSystem(System):
    """
    Consumes SnakeDirectionIntent from ActionBufferComponent and updates SnakeBodyComponent direction.
    """
    async def update(self, world: World, dt: float) -> None:
        buffers = world.get_components(ActionBufferComponent)
        bodies = world.get_components(SnakeBodyComponent)

        for entity_id, buffer in buffers.items():
            if entity_id not in bodies:
                continue

            # Process one intent per tick
            intent = buffer.dequeue()
            if intent and intent.type == "snake_direction":
                snake = bodies[entity_id]
                new_dir = intent.direction

                # Prevent 180 degree turn
                current_dir = snake.direction
                if (new_dir[0] + current_dir[0] != 0) or (new_dir[1] + current_dir[1] != 0):
                    snake.direction = new_dir

                buffer.last_executed_intent = intent

@Registry.register_system(phase=SystemPhase.INTERNAL_PHYSICS, modes=[EngineMode.GYMNASIUM, EngineMode.PRODUCTION])
class SnakeLocomotionSystem(System):
    """
    Moves the snake.
    """
    async def update(self, world: World, dt: float) -> None:
        bodies = world.get_components(SnakeBodyComponent)
        for entity_id, snake in bodies.items():
            if not snake.segments or snake.is_dead:
                continue

            head = snake.segments[0]
            dx, dy = snake.direction
            new_head = (head[0] + dx, head[1] + dy)

            snake.segments.insert(0, new_head)

            if snake.grow_pending > 0:
                snake.grow_pending -= 1
            else:
                snake.segments.pop()

@Registry.register_system(phase=SystemPhase.INTERNAL_PHYSICS, modes=[EngineMode.GYMNASIUM, EngineMode.PRODUCTION])
class SnakeCollisionSystem(System):
    """
    Handles collisions with walls, self, and food.
    """
    async def update(self, world: World, dt: float) -> None:
        bodies = world.get_components(SnakeBodyComponent)
        foods = world.get_components(SnakeFoodComponent)
        configs = world.get_components(SnakeConfigComponent)
        rewards = world.get_components(RewardComponent)

        # Get board size from first config found
        config_entity = None
        if configs:
            config_entity = next(iter(configs.values()))

        w = config_entity.board_width if config_entity else 10
        h = config_entity.board_height if config_entity else 10

        for entity_id, snake in bodies.items():
            if not snake.segments or snake.is_dead:
                continue

            head = snake.segments[0]

            # Wall Collision
            if head[0] < 0 or head[0] >= w or head[1] < 0 or head[1] >= h:
                snake.is_dead = True
                if entity_id in rewards:
                    rewards[entity_id].current_reward = -10.0
                continue

            # Self Collision (head hits any other segment)
            if head in snake.segments[1:]:
                snake.is_dead = True
                if entity_id in rewards:
                    rewards[entity_id].current_reward = -10.0
                continue

            # Food Collision
            eaten_food_id = None
            for food_id, food in foods.items():
                if food.position == head:
                    eaten_food_id = food_id
                    break

            if eaten_food_id is not None:
                snake.grow_pending += 1

                # Move food to random valid location
                all_segments = set()
                for s in bodies.values():
                    all_segments.update(s.segments)

                # Try random placement first for efficiency
                placed = False
                for _ in range(100):
                    fx = random.randint(0, w - 1)
                    fy = random.randint(0, h - 1)
                    if (fx, fy) not in all_segments:
                        foods[eaten_food_id].position = (fx, fy)
                        placed = True
                        break

                # If random failed (nearly full board), scan all spots
                if not placed:
                    empty_spots = []
                    for x in range(w):
                        for y in range(h):
                            if (x, y) not in all_segments:
                                empty_spots.append((x, y))

                    if empty_spots:
                        foods[eaten_food_id].position = random.choice(empty_spots)
                    else:
                        # Board full - Win condition?
                        # For now, just leave food where it is (under snake) or remove it.
                        # We'll leave it, effectively pausing food spawn.
                        pass

                if entity_id in rewards:
                    rewards[entity_id].current_reward = 10.0

@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.GYMNASIUM, EngineMode.PRODUCTION])
class SnakeIngestionSystem(System):
    """
    Reads game state and produces an observation.
    """
    async def update(self, world: World, dt: float) -> None:
        bodies = world.get_components(SnakeBodyComponent)
        foods = world.get_components(SnakeFoodComponent)
        configs = world.get_components(SnakeConfigComponent)
        perceptions = world.get_components(PerceptionComponent)

        config = None
        if configs:
            config = next(iter(configs.values()))
        w = config.board_width if config else 10
        h = config.board_height if config else 10

        food_pos = (0, 0)
        if foods:
             food_pos = next(iter(foods.values())).position

        for entity_id, perception in perceptions.items():
            # Only generate observation if this entity is playing snake (has body)
            if entity_id in bodies:
                snake = bodies[entity_id]

                state = {
                    "snake_segments": list(snake.segments), # Copy list
                    "snake_direction": snake.direction,
                    "food_position": food_pos,
                    "board_width": w,
                    "board_height": h,
                    "is_dead": snake.is_dead
                }

                obs = Observation(
                    source_node="SnakeIngestionSystem",
                    data_type="game_state",
                    content=state,
                    metadata={}
                )
                perception.add_observation("game_state", obs)
