# System Implementation Guide

This guide details how to create, register, and optimize new ECS Systems within the Serpentine Engine.

## 1. The Anatomy of a System

A System is a logic container that iterates over Entities possessing specific Components. It has no state of its own (ideally) and operates purely on Component data.

### 1.1. Base Class
All systems must inherit from `core.system.System`.

```python
from core.system import System
from core.world import World

class MySystem(System):
    async def update(self, world: World, dt: float):
        pass
```

## 2. Registration & Discovery

To be loaded by the engine, a system must be decorated with `@register_system`.

### 2.1. The Decorator
```python
from core.registry import register_system
from core.enums import Phase, EngineMode

@register_system(
    name="MyPhysicsSystem",
    phase=Phase.INTERNAL_PHYSICS,
    dependencies=["TransformComponent", "VelocityComponent"],
    mode=[EngineMode.PLAY, EngineMode.GYMNASIUM]
)
class MyPhysicsSystem(System):
    ...
```

*   **name**: Unique identifier.
*   **phase**: When in the loop this system runs (INPUT -> PERCEPTION -> PHYSICS -> COGNITION -> EXECUTION).
*   **dependencies**: List of Component names required for this system to function (informational).
*   **mode**: List of modes in which this system is active. Omit to run in all modes.

## 3. The Update Loop

The `update` method is where the magic happens. It is `async` to allow for non-blocking I/O (e.g., network calls, async file writes), though most systems will be CPU-bound.

### 3.1. Iterating Entities
Use `world.get_entities_with()` to find relevant entities efficiently.

```python
async def update(self, world: World, dt: float):
    # Get all entities that have BOTH Transform and Velocity
    # This query is cached and optimized by the World.
    entities = world.get_entities_with(TransformComponent, VelocityComponent)

    for entity, (transform, velocity) in entities:
        # Apply physics
        transform.x += velocity.vx * dt
        transform.y += velocity.vy * dt
```

### 3.2. Creating/Destroying Entities
*   **Create**: `new_entity = world.create_entity()`
*   **Destroy**: `world.destroy_entity(entity)`
    *   *Note*: Destruction is deferred to the end of the tick in some ECS implementations, but in Serpentine it is immediate. Be careful modifying the list you are iterating over.

## 4. Best Practices

### 4.1. Avoid Internal State
Do not store entity data in `self`. Store it in Components.
*   *Bad*: `self.entity_positions = {}`
*   *Good*: `world.get_component(entity, TransformComponent)`

### 4.2. Async Etiquette
*   **Do not block**: Avoid `time.sleep()`. Use `await asyncio.sleep()`.
*   **CPU Bound**: If you have a heavy calculation (e.g., pathfinding), consider offloading it to a thread executor if it causes frame drops.

### 4.3. Error Handling
Wrap critical logic in `try/except` blocks. If a system crashes, it should log the error but ideally not bring down the entire engine loop (unless critical).

## 5. Example: Health Regeneration System

```python
@register_system(
    name="HealthRegenSystem",
    phase=Phase.GAME_LOGIC,
    mode=[EngineMode.PLAY]
)
class HealthRegenSystem(System):
    async def update(self, world: World, dt: float):
        # Query entities with Health but NOT Dead
        for entity, (health,) in world.get_entities_with(HealthComponent):
            if health.current < health.max and health.is_alive:
                health.current += health.regen_rate * dt
```
