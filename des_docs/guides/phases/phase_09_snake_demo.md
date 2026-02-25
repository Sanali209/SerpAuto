# Phase 9: Sample Project (Snake AI) Guide

This guide covers the reference implementation of a complete RL loop within the Serpentine Engine.

## 1. Objectives
- **Demo**: Show end-to-end integration of Perception, Mind, and Action.
- **Physics**: Implement basic collision and locomotion systems.
- **Gym Integration**: Bridge Serpentine World into Gymnasium OpenAI interface.

## 2. Technical Prerequisites & Architecture
- [**Gymnasium Mode Guide**](../gym_mode.md)

## 3. Implementation Status

### 9.1 Game Simulation
- [ ] **SnakeBodyComponent**: Linked-list behavior for segments.
- [ ] **LocomotionSystem**: Per-tick movement and direction handling.
- [ ] **CollisionSystem**: Death and Growth logic.

### 9.2 Agent Logic
- [ ] **InternalGridPerception**: Direct observation node for the snake.
- [ ] **ChangeDirectionAction**: Mapping logical intents to world physics.

### 9.3 RL Bridge
- [ ] **Gym Wrapper**: Standard `env.step` and `env.reset` integration.
- [ ] **Visualization**: GUI monitor for seeing the snake's decision-making.
- [ ] **Verification**: Training success confirmed with PPO/A2C.

### 🛠️ Web Insights & Advanced Patterns
> [!TIP]
> **RL Vectorization**: When training the Snake AI, use `Gymnasium.vector` to run 64+ snake environments in parallel. This exponentially increases sample efficiency and ensures the model generalizes to different wall patterns.
> - **Reward Shaping**: To avoid the "infinite loop" trap (circling without eating), penalize distance to the food at every step, but normalize the reward to prevent it from overwhelming the "win" condition of eating.

### 🔄 Consolidation Hook: Unified Dataflow (Commands)
- **Goal**: Test the Intent -> Command abstraction in a controlled sim.
- **Action**: Map "SNAKE_UP" and other intents to both internal physics and (optionally) external keyboard commands to verify bridge consistency and standard dataflow.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 8 backlog: `des_docs/planning/backlogs/phase_08_backlog.md`.
- **Output**: Save remaining demo/integration tasks and technical debt to: `des_docs/planning/backlogs/phase_09_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Separate snake logic, environment bridging, and DPG visualization into distinct modules.
- **Complexity**: Use clear data classes for snake state to avoid bulky dictionary manipulation.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_snake_sim.py`.
- **Regression Check**: Verify snake growth logic does not degrade performance as body length increases.

## 6. Phase Completion Criteria
- [ ] Snake reaches length 20 in 80% of autonomous runs.
- [ ] `env.step` latency is < 1ms in uncapped Gymnasium mode.
- [ ] Collision events trigger immediate `RewardComponent` updates.

## 7. Execution Logging & Monitoring
- **Logs**: Record snake game events (Eat/Death) in `snake_project.log` via **Loguru**.
- **Metrics**: Track average score and survival time in the RL dashboard and display live summary via **Rich.Table**.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `sequential-thinking`: Refine snake perception nodes and reward models.
    - `web-search`: Fine-tune PPO hyperparameters based on industry benchmarks.
