import unittest
import asyncio
from core.world import World
from systems.games.snake import SnakeLocomotionSystem, SnakeCollisionSystem, GRID_WIDTH, GRID_HEIGHT
from components.snake import GridPositionComponent, SnakeBodyComponent, SnakeColliderComponent
from components.internal import VelocityComponent, RewardComponent

class TestSnakeSample(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.loco_sys = SnakeLocomotionSystem()
        self.col_sys = SnakeCollisionSystem()

        # Setup Snake Entity
        self.snake = self.world.add_entity()
        self.world.add_component(self.snake, GridPositionComponent(x=5, y=5))
        self.world.add_component(self.snake, SnakeBodyComponent(length=3, body_segments=[]))
        self.world.add_component(self.snake, VelocityComponent(vx=1, vy=0)) # Moving Right
        self.world.add_component(self.snake, SnakeColliderComponent(type="head"))
        self.world.add_component(self.snake, RewardComponent())

    def test_locomotion(self):
        """Test snake moves and updates tail."""
        asyncio.run(self.loco_sys.update(self.world, 0.1))

        pos = self.world.get_component(self.snake, GridPositionComponent)
        body = self.world.get_component(self.snake, SnakeBodyComponent)

        # Head moved right (5 -> 6)
        self.assertEqual(pos.x, 6)
        self.assertEqual(pos.y, 5)

        # Body recorded old head position
        self.assertEqual(len(body.body_segments), 1)
        self.assertEqual(body.body_segments[0], (5, 5))

    def test_eat_apple(self):
        """Test collision with apple increases length and reward."""
        # Spawn apple at (6, 5) - where snake will move
        apple = self.world.add_entity()
        self.world.add_component(apple, GridPositionComponent(x=6, y=5))
        self.world.add_component(apple, SnakeColliderComponent(type="apple"))

        # Move snake onto apple
        asyncio.run(self.loco_sys.update(self.world, 0.1)) # Head is now at (6, 5)

        # Run Collision Logic
        asyncio.run(self.col_sys.update(self.world, 0.1))

        # Verify
        body = self.world.get_component(self.snake, SnakeBodyComponent)
        reward = self.world.get_component(self.snake, RewardComponent)

        self.assertEqual(body.length, 4) # 3 + 1
        self.assertEqual(reward.current_reward, 10.0)

        # Verify old apple removed/respawned (Entity ID usually persists in this simple logic, just pos changes)
        # But we actually respawn the apple (change its pos) in the system
        apple_pos = self.world.get_component(apple, GridPositionComponent)
        self.assertNotEqual((apple_pos.x, apple_pos.y), (6, 5)) # Should have moved

    def test_wall_collision(self):
        """Test wall collision resets game and penalizes."""
        # Teleport to edge
        pos = self.world.get_component(self.snake, GridPositionComponent)
        pos.x = GRID_WIDTH - 1 # 9
        pos.y = 5

        # Move right (into wall x=10)
        asyncio.run(self.loco_sys.update(self.world, 0.1)) # pos.x becomes 10

        # Run Collision
        asyncio.run(self.col_sys.update(self.world, 0.1))

        pos = self.world.get_component(self.snake, GridPositionComponent)
        reward = self.world.get_component(self.snake, RewardComponent)
        body = self.world.get_component(self.snake, SnakeBodyComponent)

        # Should be reset to center
        self.assertEqual(pos.x, GRID_WIDTH // 2)
        self.assertEqual(pos.y, GRID_HEIGHT // 2)
        self.assertEqual(body.length, 3)
        self.assertEqual(reward.current_reward, -10.0)

if __name__ == '__main__':
    unittest.main()
