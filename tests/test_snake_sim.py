import unittest
import asyncio
import sys
from typing import List, Tuple
from unittest.mock import MagicMock
import logging

# Mock dependencies before imports
mock_dpg = MagicMock()
mock_dpg.mvMouseButton_Left = 0
mock_dpg.mvMouseButton_Right = 1
sys.modules['dearpygui'] = MagicMock()
sys.modules['dearpygui.dearpygui'] = mock_dpg

sys.modules['mss'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()
sys.modules['moderngl'] = MagicMock()
sys.modules['glfw'] = MagicMock()
# Mock pyglm
sys.modules['glm'] = MagicMock()

# Configure logging to avoid noise
logging.basicConfig(level=logging.ERROR)

from serpentine.core.engine import SerpentineEngine, EngineMode
from serpentine.components.snake import SnakeBodyComponent, SnakeFoodComponent, SnakeConfigComponent
from serpentine.systems.snake import SnakeLocomotionSystem, SnakeCollisionSystem, SnakeIngestionSystem, SnakeActionSystem, SnakeDirectionIntent
from serpentine.perception.components import ActionBufferComponent, PerceptionComponent
from serpentine.core.world import World
from serpentine.core.env_wrapper import SerpentineGymEnv
from serpentine.components.simulation import RewardComponent

class TestSnakeSim(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = SerpentineEngine(mode=EngineMode.GYMNASIUM, target_tps=30)
        self.world = self.engine.world
        self.world.clear() # Ensure clean state

    async def test_snake_locomotion(self):
        # Setup
        snake = self.world.create_entity()
        self.world.add_component(snake, SnakeBodyComponent(segments=[(5, 5), (4, 5)], direction=(1, 0)))

        system = SnakeLocomotionSystem()

        # Test 1 tick
        await system.update(self.world, 0.1)

        comp = self.world.get_component(snake, SnakeBodyComponent)
        self.assertEqual(comp.segments[0], (6, 5)) # Moved right
        self.assertEqual(comp.segments[1], (5, 5)) # Tail follows
        self.assertEqual(len(comp.segments), 2)

    async def test_snake_collision_wall(self):
        # Setup snake at edge, moving into wall
        # Board 10x10. Max x is 9.
        snake = self.world.create_entity()
        self.world.add_component(snake, SnakeBodyComponent(segments=[(9, 5)], direction=(1, 0)))
        self.world.add_component(snake, RewardComponent())

        config = self.world.create_entity()
        self.world.add_component(config, SnakeConfigComponent(board_width=10, board_height=10))

        system = SnakeCollisionSystem()

        # Move snake into wall (10, 5) manually to simulate Locomotion having run
        comp = self.world.get_component(snake, SnakeBodyComponent)
        comp.segments[0] = (10, 5)

        await system.update(self.world, 0.1)

        self.assertTrue(comp.is_dead)
        reward_comp = self.world.get_component(snake, RewardComponent)
        self.assertEqual(reward_comp.current_reward, -10.0)

    async def test_snake_eating(self):
        snake = self.world.create_entity()
        self.world.add_component(snake, SnakeBodyComponent(segments=[(5, 5)], direction=(1, 0)))
        self.world.add_component(snake, RewardComponent())

        food = self.world.create_entity()
        self.world.add_component(food, SnakeFoodComponent(position=(5, 5)))

        config = self.world.create_entity()
        self.world.add_component(config, SnakeConfigComponent(board_width=10, board_height=10))

        system = SnakeCollisionSystem()

        await system.update(self.world, 0.1)

        comp = self.world.get_component(snake, SnakeBodyComponent)
        self.assertEqual(comp.grow_pending, 1)
        reward_comp = self.world.get_component(snake, RewardComponent)
        self.assertEqual(reward_comp.current_reward, 10.0)

        # Food should have moved
        food_comp = self.world.get_component(food, SnakeFoodComponent)
        self.assertNotEqual(food_comp.position, (5, 5))

class TestGymWrapper(unittest.TestCase):
    def test_gym_step(self):
        # This test calls 'step' which calls 'asyncio.run'.
        # This MUST be a synchronous test case.

        # Note: If running via pytest with async plugin, this might still have a loop?
        # But TestCase implies sync execution.

        env = SerpentineGymEnv(board_size=(10, 10))
        obs, _ = env.reset()

        # Initial observation should be valid
        # Snake at (2,2), (1,2), (0,2). Head at (2,2).
        # Grid at (2,2) should be 2 (Head).
        # Note: grid index is [y, x]. So grid[2, 2].
        if isinstance(obs, list):
            self.assertEqual(obs[2][2], 2)
        else:
            self.assertEqual(obs[2, 2], 2)

        # Take action RIGHT (3) -> direction (1, 0)
        # Should move to (3, 2)
        obs, reward, terminated, truncated, info = env.step(3)

        # Check new head position in observation
        if isinstance(obs, list):
            self.assertEqual(obs[2][3], 2)
        else:
            self.assertEqual(obs[2, 3], 2)
        self.assertFalse(terminated)

        # Test collision (Self kill or Wall)
        # Current head (3, 2).
        # Move up into wall?
        # (3, 2) -> UP -> (3, 1) -> UP -> (3, 0) -> UP -> (3, -1) Wall!

        env.step(0) # UP -> (3, 1)
        env.step(0) # UP -> (3, 0)
        env.step(0) # Extra step due to input delay
        obs, reward, terminated, truncated, info = env.step(0) # UP -> (3, -1) Wall!

        self.assertTrue(terminated)
        self.assertEqual(reward, -10.0)
