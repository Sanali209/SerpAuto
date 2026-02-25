# Testing Strategy & Standards

This document outlines the testing philosophy and technical standards for the Serpentine Engine.

## 1. Core Philosophy

*   **Test Asynchronously**: The engine is built on `asyncio`. Use `unittest.IsolatedAsyncioTestCase` for almost all tests involving Systems or Nodes.
*   **Mock Dependencies**: Never rely on external services (OpenAI, N8N) or hardware (Screen Capture) during unit tests.
*   **Test Data vs Logic**: Use `World` snapshots or Pydantic models to verify state transitions, not just return values.

## 2. Testing Tools

*   **Framework**: `unittest` (Standard Library)
*   **Runner**: `pytest` (Recommended for discovery and plugins)
*   **Mocking**: `unittest.mock` (`MagicMock`, `patch`, `AsyncMock`)

## 3. Unit Testing Guide

### 3.1. Testing ECS Systems
Systems are stateful and asynchronous. To test them:
1.  Setup a `World`.
2.  Create Entities with required Components.
3.  Instantiate the System.
4.  `await system.update(world, dt=0.1)`.
5.  Assert changes in Components.

```python
import unittest
from core.world import World
from systems.movement import MovementSystem

class TestMovementSystem(unittest.IsolatedAsyncioTestCase):
    async def test_entity_moves(self):
        world = World()
        entity = world.create_entity()
        world.add_component(entity, TransformComponent(x=0, y=0))
        world.add_component(entity, VelocityComponent(vx=10, vy=0))

        system = MovementSystem()
        await system.update(world, dt=1.0)

        transform = world.get_component(entity, TransformComponent)
        self.assertEqual(transform.x, 10)
```

### 3.2. Testing Behavior Tree Nodes
Nodes have a `tick(agent, blackboard)` method. Test them in isolation.

```python
class TestSequenceNode(unittest.IsolatedAsyncioTestCase):
    async def test_sequence_success(self):
        # Mock children
        child1 = AsyncMock(return_value=Status.SUCCESS)
        child2 = AsyncMock(return_value=Status.SUCCESS)

        node = SequenceNode(children=[child1, child2])
        status = await node.tick(self.agent, self.blackboard)

        self.assertEqual(status, Status.SUCCESS)
```

### 3.3. Mocking External APIs (LLMs/Network)
Use `patch` to intercept network calls.

```python
@patch("httpx.AsyncClient.post")
async def test_llm_adapter(self, mock_post):
    mock_post.return_value.json.return_value = {"choices": [{"text": "Hello"}]}

    adapter = OpenAILikeAdapter(api_key="fake")
    response = await adapter.chat("Hi")

    self.assertEqual(response, "Hello")
```

## 4. Integration Testing

### 4.1. World Snapshots
For complex interactions, serialize the World state to JSON before and after the test to verify the entire state change.

### 4.2. Scene Loading
Verify that `SceneManager` correctly reconstitutes a World from a JSON file, including all Entity UIDs and Component data.

## 5. Performance Benchmarks

*   **Decorators**: Mark slow tests with `@unittest.skipIf(os.environ.get("FAST_TESTS"), "Skipping slow test")`.
*   **Hot Paths**: Ensure the `World.get_entities_with()` query remains O(1) or O(N_components) and does not degrade with Entity count.
