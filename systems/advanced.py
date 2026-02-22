from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.spatial import TransformComponent
from components.internal import VelocityComponent, ColliderComponent, RewardComponent

@register_system(phase=Phase.INTERNAL_PHYSICS)
class InternalPhysicsSystem(System):
    """
    Simulates simple physics for internal entities (Position += Velocity * dt).
    """
    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(TransformComponent, VelocityComponent)
        for entity in entities:
            transform = world.get_component(entity, TransformComponent)
            velocity = world.get_component(entity, VelocityComponent)

            # Simple Euler integration
            transform.x += velocity.vx * dt
            transform.y += velocity.vy * dt

            # Placeholder for collision check (ColliderComponent)
            # if world.has_component(entity, ColliderComponent): ...

@register_system(phase=Phase.TELEMETRY)
class DatasetLoggerSystem(System):
    """
    Logs Perception + Action pairs for Imitation Learning (Teacher Mode).
    """
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    async def update(self, world: World, dt: float):
        # Placeholder: Fetch PerceptionComponent and ActionBufferComponent
        # Dump to JSONL/HDF5
        pass
