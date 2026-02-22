import unittest
import asyncio
from core.world import World
from core.component import BaseComponent
from core.system import System
from core.engine import SerpentineEngine

class MockComponentA(BaseComponent):
    value: int = 0

class MockComponentB(BaseComponent):
    value: str = ""

class MockSystem(System):
    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(MockComponentA)
        for entity in entities:
            comp_a = world.get_component(entity, MockComponentA)
            comp_a.value += 1

class TestECS(unittest.TestCase):
    def test_entity_creation(self):
        world = World()
        entity = world.add_entity()
        self.assertIsNotNone(entity)

    def test_component_add_get(self):
        world = World()
        entity = world.add_entity()
        comp = MockComponentA(value=10)
        world.add_component(entity, comp)

        retrieved = world.get_component(entity, MockComponentA)
        self.assertEqual(retrieved.value, 10)

    def test_get_entities_with(self):
        world = World()
        e1 = world.add_entity()
        e2 = world.add_entity()

        world.add_component(e1, MockComponentA(value=1))
        world.add_component(e1, MockComponentB(value="test"))
        world.add_component(e2, MockComponentA(value=2))

        # Both have A
        with_a = world.get_entities_with(MockComponentA)
        self.assertEqual(len(with_a), 2)

        # Only e1 has A and B
        with_ab = world.get_entities_with(MockComponentA, MockComponentB)
        self.assertEqual(len(with_ab), 1)
        self.assertIn(e1, with_ab)

    def test_engine_loop(self):
        engine = SerpentineEngine()
        system = MockSystem()
        engine.add_system(system)

        entity = engine.world.add_entity()
        comp = MockComponentA(value=0)
        engine.world.add_component(entity, comp)

        # Run engine for a short time
        async def run_test():
            engine.is_running = True
            # Simulate one update manually for testing
            await system.update(engine.world, 0.1)
            engine.is_running = False

        asyncio.run(run_test())
        self.assertEqual(comp.value, 1)

if __name__ == '__main__':
    unittest.main()
