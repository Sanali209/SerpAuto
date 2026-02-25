import logging
import asyncio
try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Gymnasium not installed. Using mock Env class.")
    class MockEnv:
        def __init__(self):
            self.action_space = None
            self.observation_space = None
        def reset(self, seed=None, options=None):
            return None, {}
        def step(self, action):
            return None, 0, False, False, {}
        def render(self):
            pass
        def close(self):
            pass

    gym = type('gym', (), {'Env': MockEnv})
    # Mock spaces
    class MockSpace:
        def __init__(self, *args, **kwargs): pass
        def sample(self): return 0
        def contains(self, x): return True

    spaces = type('spaces', (), {
        'Discrete': MockSpace,
        'Box': MockSpace
    })

try:
    import numpy as np
except ImportError:
    np = None

from serpentine.core.engine import SerpentineEngine
from serpentine.core.registry import EngineMode, Registry
from serpentine.components.snake import SnakeBodyComponent, SnakeFoodComponent, SnakeConfigComponent
from serpentine.systems.snake import SnakeDirectionIntent
from serpentine.perception.components import ActionBufferComponent, PerceptionComponent
from serpentine.components.simulation import RewardComponent
from serpentine.perception.snake_nodes import InternalGridPerceptionNode
from serpentine.perception.types import Observation

logger = logging.getLogger(__name__)

class SerpentineGymEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, render_mode=None, board_size=(10, 10)):
        self.board_size = board_size

        # Define action and observation space
        # Actions: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT
        self.action_space = spaces.Discrete(4)

        # Observation: Grid of board_size
        if np:
            self.observation_space = spaces.Box(
                low=0, high=3, shape=(board_size[1], board_size[0]), dtype=np.uint8
            )
        else:
             self.observation_space = spaces.Box(low=0, high=3, shape=(1,1), dtype=int)

        self.engine = SerpentineEngine(mode=EngineMode.GYMNASIUM, target_tps=30) # Uncapped effectively if manual tick
        self.snake_entity_id = None

        # Pre-instantiate perception node
        self.perception_node = InternalGridPerceptionNode()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Reset engine state
        self.engine.world.clear()

        # Re-initialize scene
        self._setup_scene()

        self._run_tick(1.0/30.0)

        return self._get_observation(), {}

    def step(self, action):
        # Map action to Intent
        # 0=UP (0, -1), 1=DOWN (0, 1), 2=LEFT (-1, 0), 3=RIGHT (1, 0)
        direction_map = {
            0: (0, -1),
            1: (0, 1),
            2: (-1, 0),
            3: (1, 0)
        }
        direction = direction_map.get(int(action), (1, 0))

        # Push intent
        if self.snake_entity_id is not None:
            buffer = self.engine.world.get_component(self.snake_entity_id, ActionBufferComponent)
            if buffer:
                intent = SnakeDirectionIntent(direction=direction)
                buffer.enqueue(intent)

        # Tick engine
        self._run_tick(1.0/30.0)

        # Extract results
        obs = self._get_observation()
        reward = self._get_reward()
        terminated = self._is_terminated()
        truncated = False # Time limit handled by wrapper or config

        return obs, reward, terminated, truncated, {}

    def _run_tick(self, dt: float):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We are in an async context (e.g. testing).
            # We cannot use asyncio.run.
            # This is tricky. We should probably await if this was an async method.
            # But step() is sync.
            # For now, we assume this environment is used synchronously.
            # If used in async test, the test must handle the engine loop manually or use a separate thread.
            raise RuntimeError("SerpentineGymEnv.step() called from running event loop. This environment is synchronous.")

        asyncio.run(self.engine.tick(dt))

    def _setup_scene(self):
        # Create Config
        config = self.engine.world.create_entity()
        self.engine.world.add_component(
            config,
            SnakeConfigComponent(board_width=self.board_size[0], board_height=self.board_size[1])
        )

        # Create Food
        food = self.engine.world.create_entity()
        self.engine.world.add_component(
            food,
            SnakeFoodComponent(position=(5, 5))
        )

        # Create Snake
        self.snake_entity_id = self.engine.world.create_entity()
        self.engine.world.add_component(self.snake_entity_id, SnakeBodyComponent(segments=[(2, 2), (1, 2), (0, 2)], direction=(1, 0)))
        self.engine.world.add_component(self.snake_entity_id, ActionBufferComponent())
        self.engine.world.add_component(self.snake_entity_id, PerceptionComponent())
        self.engine.world.add_component(self.snake_entity_id, RewardComponent())

    def _get_observation(self):
        if self.snake_entity_id is None:
            if np: return np.zeros(self.board_size, dtype=np.uint8)
            return []

        perception = self.engine.world.get_component(self.snake_entity_id, PerceptionComponent)
        if not perception:
            if np: return np.zeros(self.board_size, dtype=np.uint8)
            return []

        game_state_obs = perception.get_observation("game_state")
        if not game_state_obs:
            if np: return np.zeros(self.board_size, dtype=np.uint8)
            return []

        # Process through node
        grid_obs = self.perception_node.process(game_state_obs)
        if grid_obs and grid_obs.content is not None:
            return grid_obs.content

        if np: return np.zeros(self.board_size, dtype=np.uint8)
        return [[0]*self.board_size[0] for _ in range(self.board_size[1])]

    def _get_reward(self):
        if self.snake_entity_id is None:
            return 0.0

        reward_comp = self.engine.world.get_component(self.snake_entity_id, RewardComponent)
        if reward_comp:
            val = reward_comp.current_reward
            reward_comp.current_reward = 0.0 # Reset accumulator
            return val
        return 0.0

    def _is_terminated(self):
        if self.snake_entity_id is None:
            return True

        snake = self.engine.world.get_component(self.snake_entity_id, SnakeBodyComponent)
        if snake and snake.is_dead:
            return True
        return False
