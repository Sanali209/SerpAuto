# Continuous Learning (Actor-Learner) Mode

## 1. Overview
The **Continuous Learning Mode** (also known as Actor-Learner Mode) allows agents to learn from real-world environments (Web browsers, Desktop OS) where time cannot be accelerated and I/O delays are prevalent. It enables "online" reinforcement learning by collecting experience during production tasks and updating the agent's model "on the fly" without stopping the engine.

---

## 2. Architecture: The Actor-Learner Split
To prevent heavy machine learning computations from blocking the real-time engine loop, the architecture is split into two independent processes.

### 2.1. The Actor (Serpentine Engine)
*   **Role**: Executes the main loop (typically at 20-30 TPS).
*   **Responsibility**: Perception, decision-making via localized models (ONNX/Lite-weights), and action execution.
*   **Data Collection**: The `ReplayBufferSystem` captures tuples of `[State, Action, Reward, Next State]` and pushes them to shared storage (Redis, SQLite, or JSONL).
*   **Model Versioning**: Every transition is tagged with the current model version to prevent "stale policy" destabilization during off-policy learning.

### 2.2. The Learner (Training Loop)
*   **Role**: Background process (often on a GPU).
*   **Responsibility**: Batch training using algorithms like PPO, SAC, or DQN.
*   **Model Export**: Periodically exports optimized weights to a file (e.g., `brain_v2.onnx`) for the Actor to consume.

---

## 3. Handling I/O Delays: The Async Lock
In real-world environments, actions (like clicking a button) do not produce immediate state changes. To handle this, agents use a state-machine logic within their `BrainComponent`.

### 3.1. Agent States
*   **IDLE**: Available for tasks.
*   **THINKING**: Decision in progress.
*   **WAITING_FOR_IO**: Action has been sent; waiting for the environment (e.g., page load) to stabilize.
*   **READY_TO_LEARN**: New state has been sensed; rewards can now be calculated.

### 3.2. Visual Stability Check
The `SensoryInputSystem` monitors the environment's "Delta" (change over time). The agent remains in `WAITING_FOR_IO` until the environment stabilizes (Delta approaches zero), ensuring the next observation (`S_t+1`) is accurate and not mid-animation.

---

## 4. Implementation Details

### 4.1. Components
```python
class BrainComponent(BaseComponent):
    status: Literal["IDLE", "THINKING", "WAITING_FOR_IO", "READY_TO_LEARN"] = "IDLE"
    last_state: Any = None      # Stores S_t
    last_action: Any = None     # Stores A_t
    current_model_tag: str = "v1.0"
```

### 4.2. Hot-Swapping Mechanism
The `ONNXInferenceNode` implements a **File Watcher** pattern.
1.  The Learner process writes a new `.onnx` file.
2.  The Actor's inference node detects the file change (hash/timestamp).
3.  The node reloads weights into memory during the agent's `WAITING_FOR_IO` phase.
4.  The next decision is made using the upgraded model without engine restarts.

---

## 5. Use Case: Match-3 Browser Game
1.  **Perception**: `YOLONode` maps the board pixels to an 8x8 matrix.
2.  **Action**: Agent swaps two gems.
3.  **Wait**: `SensoryInputSystem` waits for the cascade animation to stop (pixel delta = 0).
4.  **Reward**: `EnvironmentJudgeSystem` reads the score via `OCRNode` and calculates the point delta (+Reward).
5.  **Learning**: The transition is saved, and the model improves background.

---

## 6. Cross-Links
*   [Engine Overview](../architecture/engine_overview.md)
*   [Gymnasium Mode](gym_mode.md)
*   [ML Integration Insights](../api_ml/ml_integration_insights.md)