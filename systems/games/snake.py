import random
from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.snake import GridPositionComponent, SnakeBodyComponent, SnakeColliderComponent
from components.internal import VelocityComponent, RewardComponent

GRID_WIDTH = 10
GRID_HEIGHT = 10

@register_system(phase=Phase.INTERNAL_PHYSICS)
class SnakeLocomotionSystem(System):
    """
    Moves the snake head and updates the body segments.
    """
    async def update(self, world: World, dt: float):
        # In a real game, we'd use an accumulator for fixed timesteps (e.g. move every 0.2s)
        # For simplicity in this architectural sample, we assume 1 Tick = 1 Step
        # (controlled by Engine tick_rate in Production/Architect, or uncapped in Gym)

        entities = world.get_entities_with(GridPositionComponent, SnakeBodyComponent, VelocityComponent)
        for ent in entities:
            pos = world.get_component(ent, GridPositionComponent)
            body = world.get_component(ent, SnakeBodyComponent)
            vel = world.get_component(ent, VelocityComponent)

            # 1. Record current head pos to body start
            body.body_segments.insert(0, (pos.x, pos.y))

            # 2. Trim tail
            if len(body.body_segments) > body.length:
                body.body_segments.pop()

            # 3. Move head
            pos.x += int(vel.vx)
            pos.y += int(vel.vy)

@register_system(phase=Phase.INTERNAL_PHYSICS)
class SnakeCollisionSystem(System):
    """
    Handles rules: Apple -> Grow, Wall/Body -> Die/Reset.
    """
    async def update(self, world: World, dt: float):
        # Find Head
        head_ent = None
        head_pos = None
        snake_body = None
        reward_comp = None

        # Optimization: We assume single player for this sample
        heads = world.get_entities_with(SnakeBodyComponent, GridPositionComponent)
        if not heads:
            return

        head_ent = list(heads)[0]
        head_pos = world.get_component(head_ent, GridPositionComponent)
        snake_body = world.get_component(head_ent, SnakeBodyComponent)
        reward_comp = world.get_component(head_ent, RewardComponent) # Optional

        current_reward = -0.1 # Step penalty

        # 1. Wall Collision
        if (head_pos.x < 0 or head_pos.x >= GRID_WIDTH or
            head_pos.y < 0 or head_pos.y >= GRID_HEIGHT):
            self.reset_game(world, head_ent, snake_body, head_pos)
            current_reward = -10.0
            if reward_comp: reward_comp.current_reward = current_reward
            return

        # 2. Body Collision
        if (head_pos.x, head_pos.y) in snake_body.body_segments:
            self.reset_game(world, head_ent, snake_body, head_pos)
            current_reward = -10.0
            if reward_comp: reward_comp.current_reward = current_reward
            return

        # 3. Apple Collision
        # Find apple entity
        apples = world.get_entities_with(SnakeColliderComponent, GridPositionComponent)
        apple_ent = None
        for ent in apples:
            collider = world.get_component(ent, SnakeColliderComponent)
            if collider.type == "apple":
                a_pos = world.get_component(ent, GridPositionComponent)
                if a_pos.x == head_pos.x and a_pos.y == head_pos.y:
                    apple_ent = ent
                    break

        if apple_ent:
            # Eat Apple
            snake_body.length += 1
            current_reward = 10.0

            # Respawn Apple
            # Simple random logic (might spawn on body, simple check needed)
            a_pos = world.get_component(apple_ent, GridPositionComponent)
            a_pos.x = random.randint(0, GRID_WIDTH - 1)
            a_pos.y = random.randint(0, GRID_HEIGHT - 1)

        if reward_comp:
            reward_comp.current_reward = current_reward
            reward_comp.cumulative_reward += current_reward

    def reset_game(self, world, head_ent, body, pos):
        """Resets snake state."""
        body.length = 3
        body.body_segments = []
        pos.x = GRID_WIDTH // 2
        pos.y = GRID_HEIGHT // 2
        # Also need to reset velocity? Maybe.
