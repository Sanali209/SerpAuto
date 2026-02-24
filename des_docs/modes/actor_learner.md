# Actor-Learner Mode (Continuous Learning)

## 1. Overview
This mode targets "Online Learning" scenarios where the agent learns from real-time interactions with a slow environment (like a web browser or a desktop app).

## 2. Architecture: Split Process
To prevent heavy ML training from blocking the game loop, we split the architecture:
*   **Actor (The Engine)**: Runs the ECS loop. Collects experience. Executes the policy.
*   **Learner (The Trainer)**: A separate process (potentially on a different GPU node). Consumes experience, updates weights.

## 3. The I/O Lock
Real-world actions (clicking a link) take time.
*   **State Machine**:
    *   `IDLE`: Ready to act.
    *   `WAITING_FOR_IO`: Action sent, waiting for page load.
    *   `READY_TO_LEARN`: Page loaded, new state captured.
*   **Stability Check**: The `PerceptionSystem` monitors pixel deltas. It only signals `READY_TO_LEARN` when the screen stabilizes (animations stop).

## 4. Hot-Swapping
The Learner periodically saves a new `.onnx` model. The Actor's `InferenceNode` detects the file change and reloads the weights instantly, allowing the agent to get "smarter" during a long session without restarting.
