# Behavior Tree Guide

This guide explains how to use the Serpentine Behavior Tree (BT) system, focusing on the asynchronous execution model and the standard node library.

## 1. The Tick Cycle

The BT is executed by the `AI_BrainSystem` during the **COGNITION** phase of the engine loop.

```python
async def update(self, world, dt):
    for entity in agents:
        status = await brain.bt_root.tick(world, entity)
```

### The `Status` Enum
Every node **must** return one of these states:

*   **SUCCESS**: The task completed successfully.
*   **FAILURE**: The task failed.
*   **RUNNING**: The task is still in progress (e.g., waiting for HTTP response or Timer).

---

## 2. Asynchronous Execution (Async Nodes)

Since Serpentine runs on `asyncio`, nodes can perform non-blocking I/O.

### How to write an Async Node
If your node needs to wait for something (like an LLM response), it should spawn a task and return `RUNNING`.

```python
class MyAsyncNode(BehaviorTreeNode):
    def __init__(self):
        self.task = None

    async def tick(self, world, entity) -> Status:
        # 1. Check if we are already running
        if self.task and not self.task.done():
            return Status.RUNNING

        # 2. Check if we just finished
        if self.task and self.task.done():
            result = self.task.result()
            self.task = None # Reset
            return Status.SUCCESS if result else Status.FAILURE

        # 3. Start new task
        self.task = asyncio.create_task(self.do_heavy_work())
        return Status.RUNNING
```

**CRITICAL RULE**: Do not use `time.sleep()`. Use `await asyncio.sleep()`. However, inside a `tick()`, you usually want to return `RUNNING` instead of `await`-ing, to allow the rest of the engine (Physics, Rendering) to proceed.

---

## 3. Standard Node Library

### Control Flow
*   **Sequence**: Runs children in order. Fails if *any* child fails. (AND logic).
*   **Selector**: Runs children in order. Succeeds if *any* child succeeds. (OR logic).
*   **Parallel**: Runs children concurrently.

### Decorators
*   **Inverter**: Flips Success <-> Failure.
*   **Succeeder**: Ignores failure.
*   **RepeatUntilFail**: Useful for loops.

### Utility
*   **WaitNode(seconds)**: Returns `RUNNING` for N seconds.
*   **CheckBlackboardVariable**: Condition check.
*   **SetBlackboardVariable**: Modify memory.
