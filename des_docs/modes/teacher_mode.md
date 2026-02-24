# Teacher Mode (Imitation Learning & Behavioral Cloning)

## 1. Overview
Teacher Mode turns the Serpentine Engine into a high-fidelity data collection studio. In this mode, a human operator (The Teacher) takes control of an agent to perform a specific task. The engine records every tick of the simulation, capturing the "State -> Action" pairs necessary for Imitation Learning (Behavioral Cloning).

## 2. Architecture: The Recording Loop

Unlike Play Mode, where the goal is entertainment, Teacher Mode prioritizes data integrity and labeling.

### 2.1. Active Systems
*   **HumanInputSystem**: Captures keyboard/mouse events and injects them into the `ActionBufferComponent` of the puppet agent.
*   **DatasetLoggerSystem**: The core component of this mode. It subscribes to the engine loop and serializes the state of the world + the action taken at the end of every tick.
*   **AI_BrainSystem**: *Disabled* or running in "Shadow Mode" (predicting but not acting) to compare model vs. human performance.

### 2.2. The Data Format (HDF5 / JSONL)
We use different storage backends depending on the domain:
*   **HDF5 (High Performance)**: For computer vision tasks (Screenshots + Actions). Efficiently stores dense arrays.
*   **JSONL (Text/Web)**: For DOM-based agents. Stores the HTML tree and the clicked XPath selector.

**Example Record:**
```json
{
  "tick": 1405,
  "perception": {
    "screenshot_path": "data/session_01/frame_1405.jpg",
    "dom_elements": [...]
  },
  "expert_action": {
    "type": "CLICK",
    "x": 500,
    "y": 300
  },
  "metadata": {
    "task_id": "login_flow",
    "operator_quality": "expert"
  }
}
```

## 3. Workflow: From Demonstration to Model

### Step 1: Scenario Setup
The developer loads a `Blueprint` (e.g., "E-commerce Parser") and spawns the agent in a controlled environment (Docker container with a browser).

### Step 2: Live Recording
1.  Operator presses `[REC]`.
2.  Operator performs the task (navigates to URL, solves CAPTCHA, scrapes price).
3.  If the operator makes a mistake, they press `[Backtrack]` (rewind time 5 seconds) to overwrite the bad data.
4.  Operator presses `[STOP]`.

### Step 3: Dataset Review (The Labeling GUI)
The DPG Interface provides a timeline view of the session. The user can:
*   **Replay**: Watch the recording.
*   **Filter**: Remove "Idling" frames where the operator was inactive.
*   **Augment**: Add noise or crop the images to increase dataset robustness.

## 4. Integration with Training
Once the dataset is finalized, it is fed into the Training Pipeline (PyTorch/YOLO).
*   **Goal**: Train a policy network `π(s) -> a` that mimics the human.
*   **Validation**: The trained model is plugged back into the engine in `Gymnasium Mode` to verify if it can solve the task autonomously.

---

## 5. Shadow Mode (Human-in-the-Loop Validation)
After training, we can run Teacher Mode again with the AI model active but disconnected from the controls.
*   **Human**: Controls the agent.
*   **AI**: Predicts an action every tick.
*   **Engine**: Compares `HumanAction` vs `AIAction`.
*   **Metric**: If `Divergence > Threshold`, the frame is flagged as a "Edge Case" that needs more training data. This is crucial for **Active Learning**.
