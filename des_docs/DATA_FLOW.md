# Data Flow Architecture

This document traces the lifecycle of data as it moves through the Serpentine Engine.

## 1. The Feedback Loop (Sense -> Think -> Act)

The engine implements a classic Cybernetic Loop:

```
[ World / OS ]  <-- (Changes) <--  [ Actions ]
      |                                 ^
      | (Raw Data)                      | (Intent)
      v                                 |
[ Perception ]  --> (Context) -->  [ Brain ]
```

---

## 2. Detailed Data Trace

### Step 1: Ingestion (Perception)
*   **Source**: `ScreenCaptureNode` (Pixels), `DOMParserNode` (HTML).
*   **Process**:
    1.  Raw data enters the pipeline.
    2.  Filters apply transformations (Crop -> Grayscale -> OCR).
    3.  **Result**: Structured JSON (e.g., `{"enemy_loc": [100, 200], "text": "Login"}`).
*   **Storage**: Stored in `PerceptionComponent.raw_context`.

### Step 2: Cognition (Brain)
*   **Input**: `PerceptionComponent` + `MemoryComponent` (Blackboard).
*   **Process**:
    1.  `AI_BrainSystem` ticks the entity's Behavior Tree.
    2.  Nodes query the Blackboard or Perception.
    3.  Nodes return `SUCCESS`, `FAILURE`, or `RUNNING`.
    4.  Leaf nodes (Action Nodes) construct `BaseAction` objects.
*   **Output**: An `Action` object (e.g., `ClickAction(x=10, y=20)`).
*   **Storage**: Pushed to `ActionBufferComponent.queue`.

### Step 3: Execution (Act)
*   **Input**: `ActionBufferComponent.queue`.
*   **Process**:
    1.  `ActionExecutionSystem` pops the next action.
    2.  Checks `target_env`:
        *   `EXTERNAL_OS`: Calls `pyautogui.click()`.
        *   `INTERNAL_ENGINE`: Modifies `TransformComponent` of a target entity.
*   **Output**: Side effect in the real world or virtual world.

---

## 3. Inter-Agent Communication (Swarm Flow)

Agents do not share memory. They communicate via Messages.

1.  **Agent A** (Scout) spots an enemy.
2.  **Logic**: `SendMessageNode` creates a message:
    *   `Topic`: "enemy_spotted"
    *   `Payload`: `{"x": 100, "y": 100}`
3.  **Storage**: Pushed to Agent A's `MailboxComponent.outbox`.
4.  **Routing (Next Tick)**:
    *   `MessageRouterSystem` scans all outboxes.
    *   Finds all agents subscribed to "enemy_spotted".
    *   **Deep Copies** the message to Agent B's `inbox`.
5.  **Agent B** (Soldier) processes:
    *   `ListenForEventNode` sees the message in `inbox`.
    *   Extracts payload to its own Blackboard.
    *   Initiates attack sequence.
