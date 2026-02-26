import random
from typing import List, Tuple, Optional, Dict
try:
    from pydantic import BaseModel
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.components.snake import SnakeBodyComponent, SnakeFoodComponent, SnakeConfigComponent
from serpentine.components.standard import StatsComponent, TransformComponent
from serpentine.components.simulation import RewardComponent
from serpentine.perception.components import ActionBufferComponent, PerceptionComponent
from serpentine.mind.intent import ChangeDirectionIntent, KeyIntent
from serpentine.perception.types import Observation

try:
    import dearpygui.dearpygui as dpg
except ImportError:
    dpg = None

@Registry.register_system(phase=SystemPhase.TELEMETRY, modes=[EngineMode.ARCHITECT, EngineMode.TEACHER], priority=10)
class SnakeRenderSystem(System):
    """
    Renders the Snake game state using DearPyGui.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)
        self.window_tag = "Snake View"
        self.draw_node_tag = "snake_draw_node"
        self.initialized = False

    async def update(self, world: World, dt: float) -> None:
        if not dpg or not dpg.is_dearpygui_running():
            return

        if not self.initialized:
            if not dpg.does_item_exist(self.window_tag):
                # Create window if not exists
                with dpg.window(tag=self.window_tag, label="Snake Game", width=600, height=600, no_scrollbar=True):
                    dpg.add_draw_node(tag=self.draw_node_tag)
            self.initialized = True

        # Check if window was closed by user
        if not dpg.does_item_exist(self.window_tag):
            self.initialized = False
            return

        # Get data
        snakes = world.get_components(SnakeBodyComponent)
        foods = world.get_components(SnakeFoodComponent)
        configs = world.get_components(SnakeConfigComponent)
        transforms = world.get_components(TransformComponent)

        if not snakes:
            return

        # Assume first snake config
        snake_id, snake = next(iter(snakes.items()))
        config = configs.get(snake_id, next(iter(configs.values()), None))

        if not config:
            return

        # Render
        dpg.delete_item(self.draw_node_tag, children_only=True)

        # Calculate scale
        w = dpg.get_item_width(self.window_tag)
        h = dpg.get_item_height(self.window_tag)

        # Subtract some padding/title bar roughly?
        # Actually dpg.get_item_width returns window width. Content region is safer.
        # But for draw node, it draws relative to window content.

        # Let's just use window dims for now.
        if w < 10 or h < 10:
            return

        grid_w = config.grid_width
        grid_h = config.grid_height

        cell_w = w / grid_w
        cell_h = (h - 20) / grid_h # Subtract title bar approx

        # Draw Background
        dpg.draw_rectangle((0, 0), (w, h), color=(0, 0, 0, 255), fill=(0, 0, 0, 255), parent=self.draw_node_tag)

        # Draw Food
        for fid, food in foods.items():
            if fid in transforms:
                fx = transforms[fid].x
                fy = transforms[fid].y

                p1 = (fx * cell_w, fy * cell_h)
                p2 = ((fx + 1) * cell_w, (fy + 1) * cell_h)

                dpg.draw_rectangle(p1, p2, color=(255, 0, 0, 255), fill=(255, 0, 0, 255), parent=self.draw_node_tag)

        # Draw Snake
        for seg in snake.segments:
            sx, sy = seg
            p1 = (sx * cell_w, sy * cell_h)
            p2 = ((sx + 1) * cell_w, (sy + 1) * cell_h)

            # Green
            dpg.draw_rectangle(p1, p2, color=(0, 255, 0, 255), fill=(0, 255, 0, 255), parent=self.draw_node_tag)


@Registry.register_system(phase=SystemPhase.INTERNAL_PHYSICS, modes=[EngineMode.GYMNASIUM, EngineMode.ARCHITECT, EngineMode.PRODUCTION], priority=20)
class SnakeActionSystem(System):
    """
    Processes ChangeDirectionIntent and updates the snake's next_direction.
    """
    async def update(self, world: World, dt: float) -> None:
        buffers = world.get_components(ActionBufferComponent)
        snakes = world.get_components(SnakeBodyComponent)

        for entity_id, buffer in buffers.items():
            if entity_id not in snakes:
                continue

            snake = snakes[entity_id]

            intent_to_process = None
            params_idx = -1

            for i, intent in enumerate(buffer.action_queue):
                if intent.type == "change_direction":
                    if isinstance(intent, ChangeDirectionIntent):
                        intent_to_process = intent
                        params_idx = i
                        break
                elif intent.type == "key":
                    if isinstance(intent, KeyIntent):
                        direction = None
                        if intent.key == "Up": direction = "UP"
                        elif intent.key == "Down": direction = "DOWN"
                        elif intent.key == "Left": direction = "LEFT"
                        elif intent.key == "Right": direction = "RIGHT"

                        if direction:
                            intent_to_process = ChangeDirectionIntent(direction=direction)
                            params_idx = i
                            break

            if intent_to_process:
                snake.next_direction = intent_to_process.direction
                buffer.last_executed_intent = intent_to_process
                del buffer.action_queue[:params_idx+1]

@Registry.register_system(phase=SystemPhase.INTERNAL_PHYSICS, modes=[EngineMode.GYMNASIUM, EngineMode.ARCHITECT, EngineMode.PRODUCTION], priority=10)
class SnakeLocomotionSystem(System):
    """
    Updates snake position based on current direction.
    """
    async def update(self, world: World, dt: float) -> None:
        snakes = world.get_components(SnakeBodyComponent)
        configs = world.get_components(SnakeConfigComponent)

        global_config = None
        if configs:
            global_config = next(iter(configs.values()))

        for entity_id, snake in snakes.items():
            if not snake.segments:
                continue

            config = configs.get(entity_id, global_config)
            if not config:
                continue

            config.last_move_time += dt
            if config.last_move_time < config.move_interval:
                continue

            config.last_move_time -= config.move_interval

            current = snake.current_direction
            next_d = snake.next_direction

            if (next_d == "UP" and current != "DOWN") or \
               (next_d == "DOWN" and current != "UP") or \
               (next_d == "LEFT" and current != "RIGHT") or \
               (next_d == "RIGHT" and current != "LEFT"):
                snake.current_direction = next_d

            head_x, head_y = snake.segments[0]
            dx, dy = 0, 0
            if snake.current_direction == "UP": dy = -1
            elif snake.current_direction == "DOWN": dy = 1
            elif snake.current_direction == "LEFT": dx = -1
            elif snake.current_direction == "RIGHT": dx = 1

            new_head = (head_x + dx, head_y + dy)
            snake.segments.insert(0, new_head)

            # Store tail pos before popping
            if len(snake.segments) > 1:
                snake.last_tail_pos = snake.segments[-1]
                snake.segments.pop()
            else:
                # Should not happen for length 1? Tail pos is head pos?
                snake.last_tail_pos = head_x, head_y # Or keep as is

@Registry.register_system(phase=SystemPhase.INTERNAL_PHYSICS, modes=[EngineMode.GYMNASIUM, EngineMode.ARCHITECT, EngineMode.PRODUCTION], priority=0)
class SnakeCollisionSystem(System):
    """
    Handles collisions (Walls, Self, Food).
    """
    async def update(self, world: World, dt: float) -> None:
        snakes = world.get_components(SnakeBodyComponent)
        foods = world.get_components(SnakeFoodComponent)
        configs = world.get_components(SnakeConfigComponent)
        rewards = world.get_components(RewardComponent)
        stats = world.get_components(StatsComponent)
        transforms = world.get_components(TransformComponent)

        global_config = None
        if configs:
            global_config = next(iter(configs.values()))

        # Build set of food positions
        food_map = {}
        for fid, food in foods.items():
            if fid in transforms:
                t = transforms[fid]
                pos = (int(t.x), int(t.y))
                food_map[pos] = fid

        for entity_id, snake in snakes.items():
            if not snake.segments:
                continue

            config = configs.get(entity_id, global_config)
            if not config:
                continue

            head = snake.segments[0]
            head_x, head_y = head

            # Check Wall Collision
            if head_x < 0 or head_x >= config.grid_width or \
               head_y < 0 or head_y >= config.grid_height:
                if entity_id in stats:
                    stats[entity_id].is_alive = False
                if entity_id in rewards:
                    rewards[entity_id].current_reward = -1.0 # Big penalty? Or just death
                continue

            # Check Self Collision
            if head in snake.segments[1:]:
                if entity_id in stats:
                    stats[entity_id].is_alive = False
                if entity_id in rewards:
                    rewards[entity_id].current_reward = -1.0
                continue

            # Check Food Collision
            if head in food_map:
                fid = food_map[head]

                # Grow snake (append last_tail_pos)
                snake.segments.append(snake.last_tail_pos)

                # Reward
                if entity_id in rewards:
                    rewards[entity_id].current_reward = 1.0 # Positive reward for eating

                # Respawn food
                # Find valid position
                valid_pos = False
                attempts = 0
                max_attempts = 100

                while not valid_pos and attempts < max_attempts:
                    rx = random.randint(0, config.grid_width - 1)
                    ry = random.randint(0, config.grid_height - 1)
                    if (rx, ry) not in snake.segments:
                        valid_pos = True
                        if fid in transforms:
                            transforms[fid].x = float(rx)
                            transforms[fid].y = float(ry)
                    attempts += 1

                if not valid_pos:
                    # Fallback: scan grid for free spot (unlikely in demo but good for robustness)
                    for y in range(config.grid_height):
                        for x in range(config.grid_width):
                            if (x, y) not in snake.segments:
                                valid_pos = True
                                if fid in transforms:
                                    transforms[fid].x = float(x)
                                    transforms[fid].y = float(y)
                                break
                        if valid_pos:
                            break
            else:
                # No food eaten.
                # Small penalty for living/time? Or 0.
                if entity_id in rewards:
                    rewards[entity_id].current_reward = -0.01 # Encourage efficiency?

@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.GYMNASIUM], priority=0)
class SnakeStateReaderSystem(System):
    """
    Reads the game state and produces an observation.
    """
    async def update(self, world: World, dt: float) -> None:
        snakes = world.get_components(SnakeBodyComponent)
        foods = world.get_components(SnakeFoodComponent)
        configs = world.get_components(SnakeConfigComponent)
        perception_components = world.get_components(PerceptionComponent)
        transforms = world.get_components(TransformComponent)

        if not snakes or not perception_components:
            return

        # Assume single player
        snake_id, snake = next(iter(snakes.items()))
        if snake_id not in perception_components:
            return

        config = configs.get(snake_id, next(iter(configs.values()), None))
        if not config:
            return

        food_pos = (-1, -1)
        if foods:
            fid, _ = next(iter(foods.items()))
            if fid in transforms:
                food_pos = (int(transforms[fid].x), int(transforms[fid].y))

        state_data = {
            "snake_segments": list(snake.segments), # Copy
            "snake_direction": snake.current_direction,
            "food_pos": food_pos,
            "grid_size": (config.grid_width, config.grid_height),
            "score": len(snake.segments)
        }

        obs = Observation(
            source_node="SnakeStateReaderSystem",
            data_type="snake_state",
            content=state_data,
            metadata={}
        )

        perception_components[snake_id].add_observation("game_state", obs)
