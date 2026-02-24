import pytest
import uuid
import asyncio
import math
from core.world import World
from core.engine_v2 import Phase
from components.spatial import TransformComponent, HierarchyComponent
from systems.transform import TransformHierarchySystem

@pytest.mark.asyncio
async def test_hierarchy_system():
    # 1. Setup World
    world = World()

    # 2. Create Parent Entity (Tank) at (100, 100)
    parent_id = world.add_entity()
    world.add_component(parent_id, TransformComponent(x=100.0, y=100.0))
    world.add_component(parent_id, HierarchyComponent())

    # 3. Create Child Entity (Turret) at (10, 0) relative to parent
    child_id = world.add_entity()
    world.add_component(child_id, TransformComponent(x=10.0, y=0.0))
    world.add_component(child_id, HierarchyComponent(parent=parent_id))

    # 4. Link Parent -> Child
    parent_hierarchy = world.get_component(parent_id, HierarchyComponent)
    parent_hierarchy.children.append(child_id)

    # 5. Run System
    system = TransformHierarchySystem()
    await system.update(world, 0.1)

    # 6. Verify Child World Position (Simple Translation)
    # Expected: Parent(100) + Child(10) = 110
    child_transform = world.get_component(child_id, TransformComponent)
    assert child_transform.world_x == 110.0
    assert child_transform.world_y == 100.0

    # 7. Move Parent and Verify Update
    parent_transform = world.get_component(parent_id, TransformComponent)
    parent_transform.local_x = 200.0 # Move tank forward

    await system.update(world, 0.1)

    # Expected: Parent(200) + Child(10) = 210
    assert child_transform.world_x == 210.0

@pytest.mark.asyncio
async def test_hierarchy_rotation():
    # 1. Setup World
    world = World()

    # 2. Create Parent (Pivot) at (0, 0)
    parent_id = world.add_entity()
    world.add_component(parent_id, TransformComponent(x=0.0, y=0.0))
    world.add_component(parent_id, HierarchyComponent())

    # 3. Create Child at (10, 0) relative to parent
    child_id = world.add_entity()
    world.add_component(child_id, TransformComponent(x=10.0, y=0.0))
    world.add_component(child_id, HierarchyComponent(parent=parent_id))

    # Link
    parent_h = world.get_component(parent_id, HierarchyComponent)
    parent_h.children.append(child_id)

    # 4. Run System (Initial Check)
    system = TransformHierarchySystem()
    await system.update(world, 0.1)
    child_t = world.get_component(child_id, TransformComponent)
    assert child_t.world_x == 10.0
    assert child_t.world_y == 0.0

    # 5. Rotate Parent 90 degrees
    parent_t = world.get_component(parent_id, TransformComponent)
    # CRITICAL FIX: Set local_rotation, not world_rotation, because the system overwrites world from local for roots.
    parent_t.local_rotation = 90.0

    await system.update(world, 0.1)

    # Expected:
    # x = 10 * cos(90) - 0 * sin(90) = 0
    # y = 10 * sin(90) + 0 * cos(90) = 10

    assert math.isclose(child_t.world_x, 0.0, abs_tol=1e-5)
    assert math.isclose(child_t.world_y, 10.0, abs_tol=1e-5)
    assert child_t.world_rotation == 90.0
