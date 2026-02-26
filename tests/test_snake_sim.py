import sys
from unittest.mock import MagicMock

# Mock dearpygui before imports
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()

import unittest
import time
try:
    import numpy as np
except ImportError:
    np = None

from serpentine.core.gym_wrapper import SerpentineGymEnv
from serpentine.components.snake import SnakeBodyComponent
from serpentine.components.standard import TransformComponent

class TestSnakeSim(unittest.TestCase):
    def setUp(self):
        if np is None:
            self.skipTest("Numpy not installed")
        try:
            self.env = SerpentineGymEnv(grid_size=(10, 10))
        except ImportError:
            self.skipTest("Gymnasium not installed")

    def tearDown(self):
        if hasattr(self, 'env'):
            self.env.close()

    def test_reset(self):
        obs, info = self.env.reset()

        # Check entities
        self.assertIsNotNone(self.env.snake_id)
        self.assertIsNotNone(self.env.food_id)

        # Check components
        snake = self.env.engine.world.get_component(self.env.snake_id, SnakeBodyComponent)
        self.assertIsNotNone(snake)
        self.assertEqual(len(snake.segments), 3)

        # Check observation shape
        self.assertEqual(obs.shape, (10, 10))

        # Check content (Head=1, Body=2, Food=3)
        self.assertTrue(np.any(obs == 1))
        self.assertTrue(np.any(obs == 2))
        self.assertTrue(np.any(obs == 3))

    def test_movement(self):
        self.env.reset()
        snake = self.env.engine.world.get_component(self.env.snake_id, SnakeBodyComponent)
        start_head = snake.segments[0]

        # Move UP (Action 0)
        # Note: Snake starts facing UP.
        obs, reward, terminated, truncated, info = self.env.step(0)

        new_head = snake.segments[0]
        self.assertEqual(new_head, (start_head[0], start_head[1] - 1))
        self.assertEqual(len(snake.segments), 3)
        self.assertFalse(terminated)

    def test_food_eating(self):
        self.env.reset()
        snake = self.env.engine.world.get_component(self.env.snake_id, SnakeBodyComponent)
        head = snake.segments[0]

        # Place food right above head
        food_pos = (head[0], head[1] - 1)

        # Move food entity
        food_transform = self.env.engine.world.get_component(self.env.food_id, TransformComponent)
        food_transform.x = float(food_pos[0])
        food_transform.y = float(food_pos[1])

        # Step UP
        obs, reward, terminated, truncated, info = self.env.step(0)

        # Check growth
        self.assertEqual(len(snake.segments), 4)
        self.assertEqual(reward, 1.0)
        self.assertFalse(terminated)

        # Check snake head is at food pos
        self.assertEqual(snake.segments[0], food_pos)

    def test_wall_collision(self):
        self.env.reset()
        snake = self.env.engine.world.get_component(self.env.snake_id, SnakeBodyComponent)

        # Teleport to top edge (0, 0) facing UP
        # Be careful not to create self collision on spawn if body is (0,1), (0,2)
        snake.segments = [(5, 0), (5, 1), (5, 2)]
        snake.current_direction = "UP"

        # Step UP -> Hit wall (y=-1)
        obs, reward, terminated, truncated, info = self.env.step(0)

        self.assertTrue(terminated)
        self.assertEqual(reward, -1.0)

if __name__ == '__main__':
    unittest.main()
