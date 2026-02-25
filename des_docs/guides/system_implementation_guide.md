# System Implementation Guide

This guide details how to implement systems in the Serpentine Engine.

## 1. Basics

A `System` is a class responsible for logic processing. It operates on entities and components stored in the `World`.

```python
from serpentine.systems.base import System
from serpentine.core.registry import Registry, SystemPhase, EngineMode

@Registry.register_system(phase=SystemPhase.INTERNAL_PHYSICS)
class MyPhysicsSystem(System):
    async def update(self, world, dt):
        # Your logic here
        pass
```

## 2. System Configuration

Systems can be configured with metadata using the `@Registry.register_system` decorator.

### Arguments

*   **phase**: The `SystemPhase` (e.g., `INPUT`, `PERCEPTION`, `INTERNAL_PHYSICS`) where this system runs.
*   **modes**: A list of `EngineMode` (e.g., `ARCHITECT`, `PRODUCTION`) where this system is active. Default: All modes.
*   **priority**: Execution order within the phase. Higher priority runs first. Default: 0.
*   **tick_rate**: (Optional) A specific update rate (TPS) for this system.

## 3. Tick Rate Adjustment

Systems can run at a different frequency than the main engine loop. This is useful for systems that don't need to update every frame (e.g., AI decision making) or need a fixed timestep (e.g., Physics).

### How it Works

If `tick_rate` is specified in the registration metadata:
1.  The engine tracks an accumulator for the system.
2.  The system's `update(world, dt)` method is called only when enough time has accumulated (`>= 1.0 / tick_rate`).
3.  The `dt` passed to `update` will be fixed at `1.0 / tick_rate`.
4.  If the engine lags, `update` may be called multiple times in a single engine tick to catch up.

### Example

```python
# This AI system runs at 10 TPS, regardless of the engine's frame rate (e.g. 60 FPS)
@Registry.register_system(phase=SystemPhase.COGNITION, tick_rate=10)
class AISystem(System):
    async def update(self, world, dt):
        # dt will always be 0.1 (1/10) here
        pass
```

### When to Use
*   **Physics**: Use a fixed `tick_rate` (e.g., 60) for stable integration.
*   **AI/Behavior Trees**: Use a lower `tick_rate` (e.g., 5-10) to save CPU cycles.
*   **Network Sync**: Use a fixed rate to match server tick rate.

### Standard Behavior
If `tick_rate` is `None` (default), the system runs every engine tick with a variable `dt` (delta time since the last frame).
