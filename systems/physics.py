from core.system import BaseSystem
from core.world import World
from components.standard import TransformComponent, VelocityComponent

class PhysicsSystem(BaseSystem):
    """Updates position based on velocity."""

    async def update(self, world: World, dt: float):
        # O(1) query thanks to caching
        entities = world.get_entities_with(TransformComponent, VelocityComponent)

        for ent in entities:
            transform = world.get_component(ent, TransformComponent)
            velocity = world.get_component(ent, VelocityComponent)

            if transform and velocity:
                transform.x += velocity.vx * dt
                transform.y += velocity.vy * dt
