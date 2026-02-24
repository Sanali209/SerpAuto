import pytest
import uuid
import asyncio
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
    world.add_component(parent_id, TransformComponent(local_x=100.0, local_y=100.0))
    world.add_component(parent_id, HierarchyComponent())

    # 3. Create Child Entity (Turret) at (10, 0) relative to parent
    child_id = world.add_entity()
    world.add_component(child_id, TransformComponent(local_x=10.0, local_y=0.0))
    world.add_component(child_id, HierarchyComponent(parent=parent_id))

    # 4. Link Parent -> Child
    parent_hierarchy = world.get_component(parent_id, HierarchyComponent)
    parent_hierarchy.children.append(child_id)

    # 5. Run System
    system = TransformHierarchySystem()
    await system.update(world, 0.1)

    # 6. Verify Child World Position
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
