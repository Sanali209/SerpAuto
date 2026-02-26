import unittest
import sys
import asyncio
from unittest.mock import MagicMock, patch

class TestSnakeSim(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create patcher for modules
        cls.modules_patcher = patch.dict(sys.modules, {
            "numpy": MagicMock(),
            "gymnasium": MagicMock(),
            "dearpygui": MagicMock(),
            "dearpygui.dearpygui": MagicMock()
        })
        cls.modules_patcher.start()

        # Configure mocks
        mock_numpy = sys.modules["numpy"]
        mock_numpy.uint8 = "uint8"
        mock_numpy.zeros = lambda shape, dtype=None: MagicMock()
        mock_numpy.any = lambda x: True

        mock_gym = sys.modules["gymnasium"]
        mock_spaces = MagicMock()
        mock_spaces.Discrete = MagicMock()
        mock_spaces.Box = MagicMock()
        mock_gym.spaces = mock_spaces

        class MockEnv:
            def reset(self, seed=None, options=None):
                return None, {}
            def step(self, action):
                return None, 0, False, False, {}
        mock_gym.Env = MockEnv

        # Import modules inside patched environment
        global SnakeBodyComponent, TransformComponent, ActionBufferComponent, KeyIntent, SerpentineGymEnv, np

        # Use importlib to reload if needed, but since we are inside setUpClass and imports were removed from top level, it should be fine.
        # However, if other tests ran before this in the same process, modules might be cached.
        # But here we are running only this test file.

        from serpentine.components.snake import SnakeBodyComponent
        from serpentine.components.standard import TransformComponent
        from serpentine.perception.components import ActionBufferComponent
        from serpentine.mind.intent import KeyIntent
        from serpentine.core.gym_wrapper import SerpentineGymEnv
        import numpy as np

    @classmethod
    def tearDownClass(cls):
        cls.modules_patcher.stop()

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.env = SerpentineGymEnv(grid_size=(10, 10))

    def tearDown(self):
        if hasattr(self, 'env'):
            self.env.close()
        if hasattr(self, 'loop'):
            self.loop.close()

    def test_reset(self):
        obs, info = self.env.reset()

        # Check components
        snake = self.env.engine.world.get_component(self.env.snake_id, SnakeBodyComponent)
        self.assertIsNotNone(snake)
        self.assertEqual(len(snake.segments), 3)

    def test_movement(self):
        self.env.reset()
        snake = self.env.engine.world.get_component(self.env.snake_id, SnakeBodyComponent)
        start_head = snake.segments[0]

        # Move UP (Action 0)
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
        self.assertEqual(snake.segments[0], food_pos)

    def test_wall_collision(self):
        self.env.reset()
        snake = self.env.engine.world.get_component(self.env.snake_id, SnakeBodyComponent)

        # Teleport to top edge (0, 0) facing UP
        snake.segments = [(5, 0), (5, 1), (5, 2)]
        snake.current_direction = "UP"

        # Step UP -> Hit wall (y=-1)
        obs, reward, terminated, truncated, info = self.env.step(0)

        self.assertTrue(terminated)
        self.assertEqual(reward, -1.0)

    def test_key_intent(self):
        """Test that KeyIntent is processed correctly."""
        self.env.reset()
        snake = self.env.engine.world.get_component(self.env.snake_id, SnakeBodyComponent)
        buffer = self.env.engine.world.get_component(self.env.snake_id, ActionBufferComponent)

        # Ensure buffer is clear
        buffer.clear()

        # Enqueue KeyIntent "Left"
        intent = KeyIntent(key="Left", action="press")
        buffer.enqueue(intent)

        # Run one tick
        async def run_tick():
            await self.env.engine._tick(0.1)

        self.env._run_async(run_tick())

        # Check snake.next_direction
        self.assertEqual(snake.next_direction, "LEFT")
        self.assertEqual(len(buffer.action_queue), 0)

if __name__ == '__main__':
    unittest.main()
