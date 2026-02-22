import unittest
import asyncio
from core.world import World
from core.system import System
from core.engine_v2 import SerpentineEngineV2, Phase
from components.spatial import TransformComponent
from components.internal import VelocityComponent

class InternalPhysicsSystem(System):
    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(TransformComponent, VelocityComponent)
        for entity in entities:
            transform = world.get_component(entity, TransformComponent)
            velocity = world.get_component(entity, VelocityComponent)
            transform.x += velocity.vx * dt
            transform.y += velocity.vy * dt

class TestV2Architecture(unittest.TestCase):
    def test_engine_phases_and_physics(self):
        engine = SerpentineEngineV2()
        physics = InternalPhysicsSystem()

        # Register physics system in the correct phase
        engine.add_system(physics, phase=Phase.INTERNAL_PHYSICS)

        entity = engine.world.add_entity()
        engine.world.add_component(entity, TransformComponent(x=0, y=0))
        engine.world.add_component(entity, VelocityComponent(vx=10, vy=5))

        # Run 1 tick manually
        async def run_tick():
            # In V2 we iterate over phases, but for unit testing a single tick
            # we can just invoke the update manually if we want to isolate
            # Or run the full engine loop for a tiny duration

            # Let's simulate the loop logic for one iteration
            dt = 0.1
            await physics.update(engine.world, dt)

        asyncio.run(run_tick())

        transform = engine.world.get_component(entity, TransformComponent)
        self.assertAlmostEqual(transform.x, 1.0) # 0 + 10 * 0.1
        self.assertAlmostEqual(transform.y, 0.5) # 0 + 5 * 0.1

if __name__ == '__main__':
    unittest.main()
