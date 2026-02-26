import asyncio
import logging
from typing import Tuple, Dict, Any, Optional

try:
    import numpy as np
except ImportError:
    np = None

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:
    # Fallback/Mock for environments without gym
    class MockGym:
        class Env:
            pass
    gym = MockGym()
    spaces = None

# Ensure snake systems are registered
import serpentine.systems.snake

from serpentine.core.engine import SerpentineEngine
from serpentine.core.registry import EngineMode, Registry
from serpentine.components.snake import SnakeBodyComponent, SnakeFoodComponent, SnakeConfigComponent
from serpentine.components.standard import TransformComponent, StatsComponent
from serpentine.components.simulation import RewardComponent
from serpentine.perception.components import ActionBufferComponent, PerceptionComponent
from serpentine.mind.intent import ChangeDirectionIntent
from serpentine.perception.nodes import InternalGridPerception

logger = logging.getLogger(__name__)

class SerpentineGymEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, render_mode=None, grid_size=(20, 20)):
        if spaces is None:
            raise ImportError("Gymnasium is not installed.")

        self.grid_w, self.grid_h = grid_size
        self.render_mode = render_mode

        # Action space: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT
        self.action_space = spaces.Discrete(4)

        # Observation space: Grid map (H, W)
        self.observation_space = spaces.Box(
            low=0, high=3, shape=(self.grid_h, self.grid_w), dtype=np.uint8
        )

        self.engine = SerpentineEngine(mode=EngineMode.GYMNASIUM)

        # Manage Event Loop
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        self.snake_id = None
        self.food_id = None
        self.perception_node = InternalGridPerception("gym_grid_node")

    def _run_async(self, coro):
        """Helper to run async methods synchronously."""
        if self.loop.is_running():
            raise RuntimeError("Cannot use synchronous SerpentineGymEnv within an existing running event loop. "
                               "Please run the environment in a separate thread or process, or use an async-compatible wrapper.")
        return self.loop.run_until_complete(coro)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Reset Engine World
        self.engine.world._entities.clear()
        self.engine.world._components.clear()
        self.engine.world._query_cache.clear()

        # Spawn Entities
        self.snake_id = self.engine.world.create_entity()

        # Snake Body
        start_x, start_y = self.grid_w // 2, self.grid_h // 2
        snake_body = SnakeBodyComponent(
            segments=[(start_x, start_y), (start_x, start_y+1), (start_x, start_y+2)],
            current_direction="UP",
            next_direction="UP"
        )
        self.engine.world.add_component(self.snake_id, snake_body)

        # Snake Config
        config = SnakeConfigComponent(
            grid_width=self.grid_w,
            grid_height=self.grid_h,
            move_interval=0.0 # Force move every tick
        )
        self.engine.world.add_component(self.snake_id, config)

        # Stats
        self.engine.world.add_component(self.snake_id, StatsComponent(is_alive=True))

        # Reward
        self.engine.world.add_component(self.snake_id, RewardComponent())

        # ActionBuffer
        self.engine.world.add_component(self.snake_id, ActionBufferComponent())

        # Perception
        self.engine.world.add_component(self.snake_id, PerceptionComponent())

        # Food Entity
        self.food_id = self.engine.world.create_entity()
        self.engine.world.add_component(self.food_id, SnakeFoodComponent())
        self.engine.world.add_component(self.food_id, TransformComponent(x=float(start_x), y=float(start_y-5)))

        # Run one tick to generate initial observation
        self._run_async(self.engine._tick(0.1))

        obs = self._get_obs()
        info = {}
        return obs, info

    def step(self, action):
        # Map action to Intent
        direction_map = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT"}
        direction = direction_map.get(int(action), "UP")

        # Enqueue Intent
        buffer = self.engine.world.get_component(self.snake_id, ActionBufferComponent)
        if buffer:
            intent = ChangeDirectionIntent(direction=direction)
            buffer.enqueue(intent)

        # Tick Engine
        self._run_async(self.engine._tick(0.1))

        obs = self._get_obs()

        # Get Reward
        reward = 0.0
        reward_comp = self.engine.world.get_component(self.snake_id, RewardComponent)
        if reward_comp:
            reward = reward_comp.current_reward
            reward_comp.current_reward = 0.0

        # Check Done
        terminated = False
        stats = self.engine.world.get_component(self.snake_id, StatsComponent)
        if stats and not stats.is_alive:
            terminated = True

        truncated = False
        info = {}

        return obs, reward, terminated, truncated, info

    def _get_obs(self):
        perception = self.engine.world.get_component(self.snake_id, PerceptionComponent)
        if not perception:
            return np.zeros((self.grid_h, self.grid_w), dtype=np.uint8)

        raw_obs = perception.get_observation("game_state")
        if not raw_obs:
            return np.zeros((self.grid_h, self.grid_w), dtype=np.uint8)

        grid_obs = self.perception_node.process(raw_obs)

        if grid_obs:
            return grid_obs.content
        return np.zeros((self.grid_h, self.grid_w), dtype=np.uint8)

    def render(self):
        if self.render_mode == "rgb_array":
            return self._get_obs()
        elif self.render_mode == "human":
            # Just print the grid
            print(self._get_obs())

    def close(self):
        self.engine.stop()
        if self.loop.is_running():
            # Should not close running loop
            pass
        else:
            self.loop.close()
