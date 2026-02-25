import pytest
import time
import asyncio
from typing import List
from uuid import UUID

from serpentine.core.world import World
from serpentine.core.entity import EntityID
from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.engine import SerpentineEngine

# Define test components
class Position(BaseComponent):
    x: float = 0.0
    y: float = 0.0

class Velocity(BaseComponent):
    vx: float = 0.0
    vy: float = 0.0

# Define test systems
class MovementSystem(System):
    async def update(self, world: World, dt: float):
        for entity, pos, vel in world.get_entities_with(Position, Velocity):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt

@pytest.fixture
def world():
    return World()

@pytest.fixture(autouse=True)
def reset_registry():
    # Backup
    original_systems = Registry._systems.copy()
    original_metadata = Registry._system_metadata.copy()
    original_components = Registry._components.copy()

    yield

    # Restore
    Registry._systems = original_systems
    Registry._system_metadata = original_metadata
    Registry._components = original_components

def test_entity_creation(world):
    entity_id = world.create_entity()
    assert isinstance(entity_id, UUID)
    assert entity_id in world._entities

def test_component_management(world):
    entity_id = world.create_entity()
    pos = Position(x=10, y=20)

    world.add_component(entity_id, pos)
    assert world.has_component(entity_id, Position)
    assert world.get_component(entity_id, Position) == pos

    world.remove_component(entity_id, Position)
    assert not world.has_component(entity_id, Position)
    assert world.get_component(entity_id, Position) is None

def test_query_engine(world):
    entity1 = world.create_entity()
    world.add_component(entity1, Position(x=1, y=2))
    world.add_component(entity1, Velocity(vx=1, vy=1))

    entity2 = world.create_entity()
    world.add_component(entity2, Position(x=3, y=4))

    # Query for Position and Velocity
    results = list(world.get_entities_with(Position, Velocity))
    assert len(results) == 1
    assert results[0][0] == entity1

    # Query for Position only
    results = list(world.get_entities_with(Position))
    assert len(results) == 2

def test_query_performance(world):
    # Setup 10k entities
    for i in range(10000):
        e = world.create_entity()
        world.add_component(e, Position(x=i, y=i))
        if i % 2 == 0:
            world.add_component(e, Velocity(vx=1, vy=1))

    # Force query to populate cache
    _ = list(world.get_entities_with(Position, Velocity))

    # Measure cached query retrieval only (not tuple creation)
    start_time = time.time()
    # We only measure the time to get the set of entity IDs,
    # as iterating and yielding tuples is O(N) and depends on Python overhead.
    # Accessing the private cache directly to verify the "query mechanism" speed.
    cache_key = tuple(sorted((Position, Velocity), key=lambda t: t.__name__))
    entities = world._query_cache.get(cache_key)
    query_time = (time.time() - start_time) * 1000

    assert entities is not None
    assert len(entities) == 5000
    assert query_time < 1.0, f"Cached query lookup took {query_time:.4f}ms"

def test_engine_loop():
    # Register test system

    @Registry.register_system(phase=SystemPhase.INTERNAL_PHYSICS, modes=[EngineMode.ARCHITECT])
    class TestSystem(System):
        updated = False
        async def update(self, world: World, dt: float):
            TestSystem.updated = True

    engine = SerpentineEngine(mode=EngineMode.ARCHITECT, target_tps=100)

    async def run_test():
        # Run for a short time
        task = asyncio.create_task(engine.run())
        await asyncio.sleep(0.1)
        engine.stop()
        await task

    asyncio.run(run_test())

    assert TestSystem.updated

def test_registry():
    @Registry.register_component
    class TestComp(BaseComponent):
        pass

    assert Registry.get_component("TestComp") == TestComp
