import asyncio
import time
from core.world import World
from systems.physics import PhysicsSystem
from systems.web import WebExtractionSystem
from components.standard import (
    TransformComponent, VelocityComponent,
    DOMNodeComponent, PayloadExtractionComponent
)

async def test_ecs():
    print("Initializing World...")
    world = World()

    # 1. Create Physics Entity
    ent1 = world.create_entity()
    world.add_component(ent1, TransformComponent(x=0, y=0))
    world.add_component(ent1, VelocityComponent(vx=10, vy=0))

    # 2. Create Web Entity
    ent2 = world.create_entity()
    world.add_component(ent2, DOMNodeComponent(attributes={"class": "price-tag"}, extracted_text="100$"))
    world.add_component(ent2, PayloadExtractionComponent())

    # 3. Create Mixed Entity (should be processed by both?)
    ent3 = world.create_entity()
    world.add_component(ent3, TransformComponent(x=10, y=10))
    world.add_component(ent3, VelocityComponent(vx=0, vy=5))
    world.add_component(ent3, DOMNodeComponent(attributes={"class": "header"}, extracted_text="Title")) # Not price-tag
    world.add_component(ent3, PayloadExtractionComponent())

    physics_sys = PhysicsSystem()
    web_sys = WebExtractionSystem()

    dt = 0.1

    # Run Physics Update
    await physics_sys.update(world, dt)

    # Check ent1
    t1 = world.get_component(ent1, TransformComponent)
    assert t1.x == 1.0 # 0 + 10 * 0.1
    print("Entity 1 Physics OK")

    # Check ent3
    t3 = world.get_component(ent3, TransformComponent)
    assert t3.y == 10.5 # 10 + 5 * 0.1
    print("Entity 3 Physics OK")

    # Run Web Update
    await web_sys.update(world, dt)

    # Check ent2
    p2 = world.get_component(ent2, PayloadExtractionComponent)
    assert p2.extracted_data.get("price") == "100$"
    assert p2.validation_status == True
    print("Entity 2 Web OK")

    # Check ent3 (class is header, not price-tag)
    p3 = world.get_component(ent3, PayloadExtractionComponent)
    assert "price" not in p3.extracted_data
    print("Entity 3 Web Logic OK")

    # Performance Test
    print("Running Performance Test (10,000 entities)...")
    count = 10000

    # Measure creation time
    start_time = time.perf_counter()
    for i in range(count):
        e = world.create_entity()
        world.add_component(e, TransformComponent())
        world.add_component(e, VelocityComponent())

    setup_time = time.perf_counter() - start_time
    print(f"Setup {count} entities took {setup_time:.4f}s")

    # Measure update time (PhysicsSystem)
    start_time = time.perf_counter()
    await physics_sys.update(world, 0.016)
    update_time = time.perf_counter() - start_time
    print(f"Update {count} entities took {update_time:.4f}s")

    # Even in pure Python, 10k items iteration + simple math should be reasonably fast
    # But Set Intersection query should be instant because of caching

    # Verify we processed them
    # Just check one random entity
    t_check = world.get_component(e, TransformComponent)
    # default vx is 0, so x won't change unless we set velocity.
    # But we want to ensure loop ran.

    assert update_time < 1.0
    print("Performance OK")

if __name__ == "__main__":
    asyncio.run(test_ecs())
