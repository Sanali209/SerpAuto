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
*   **Parallel**: Runs children concurrently.

### 🎯 Intent Nodes (Action Nodes)
In the Serpentine framework, Action Nodes do not directly trigger physical drivers (like PyAutoGUI). Instead, they produce **Intent** objects.
- **Goal**: Separation of "Thinking" from "Doing".
- **Process**: A node creates an `Intent` (e.g., `ClickIntent`) and pushes it to the agent's `ActionBufferComponent`.

### Decorators
*   **Inverter**: Flips Success <-> Failure.
*   **Succeeder**: Always returns SUCCESS (unless child is RUNNING).
*   **RepeatUntilFail**: Useful for loop logic.

### AI & Inference
*   **LLMInferenceNode**: The core cognitive node. Triggers an async call to an LLM via an AI Adapter. It handles state synchronization (`WAITING_LLM` status) and writes results to the blackboard.

### Utility
*   **WaitNode(seconds)**: Returns `RUNNING` for N seconds.
*   **SetBlackboardVariable**: Modify memory.

---

## 4. Visual Editing & Parameters

### `@register_node` Metadata
All BT nodes should be registered via the Registry V2 to appear in the [**Visual BT Editor**](../architecture/behavior_tree_editor.md).
```python
@register_node(category="Actions", icon="🖱️")
class MyActionNode(BehaviorTreeNode):
    class Params(BaseModel):
        target: str # This will automatically appear in the Inspector
```

### Selection & Inspector
When a node is selected in the visual editor, the **SelectionService** synchronized the **Inspector Window**. The Inspector uses **AutoUIBuilder** to render the `Params` Pydantic model into editable widgets.
