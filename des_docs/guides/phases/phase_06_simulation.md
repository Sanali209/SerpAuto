# Phase 6: Environment, Simulation & Teacher Mode Guide

This guide covers the simulation layer and imitation learning data collection.

## 1. Objectives
- **Hybrid Env**: Support both internal sims and external OS interaction.
- **Teacher Mode**: Human-in-the-loop data collection.
- **Shadow Mode**: Running AI predictions in parallel for validation.

## 2. Technical Prerequisites & Architecture
- [**Actor-Learner Split**](../actor_learner.md)
- [**Teacher Mode Design**](../teacher_mode.md)

## 3. Implementation Status

### 6.1 Simulation Layer
- [ ] **HumanInputSystem**: DPG-to-ECS input bridge.
- [ ] **Internal Physics**: (Basic) Velocity and collisions implemented in Phase 9.
- [ ] **Generic Router**: (Pending) Dynamic environment targeting.

### 6.2 Teacher Mode & Data
- [ ] **DatasetLogger**: State-action pair serialization to JSONL.
- [ ] **REC UI**: Recording control in the GUI.
- [ ] **Shadow Mode**: (Pending) Real-time AI loss monitoring.

### 🛠️ Web Insights & Advanced Patterns
> [!IMPORTANT]
> **Async Vectorization**: Use Gymnasium's `AsyncVectorEnv` for environments with high overhead (like CV capture) to leverage multi-core CPUs, but fall back to `SyncVectorEnv` on low-RAM systems to avoid subprocess thrashing.
> - **Zero-Copy Serialization**: When dumping datasets from Teacher Mode, use binary formats like **HDF5** or **Zarr** if the state contains large NumPy arrays (e.g., screen frames) to avoid the 10x overhead of JSON string conversion.

### 🔄 Consolidation Hook: Generic Simulation Traits
- **Goal**: Decouple evaluation logic from specific domain implementations.
- **Action**: Standardize on a universal `RewardComponent` and `GoalComponent` that any Mode (Teacher/Gym/Continuous) can ingest for reinforcement learning flows.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 5 backlog: `des_docs/planning/backlogs/phase_05_backlog.md`.
- **Output**: Save remaining simulation/training tasks and technical debt to: `des_docs/planning/backlogs/phase_06_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Separate data serialization logic (HDF5/JSONL) from core simulation step mechanics.
- **Complexity**: Use Component-based design for simulation goals to avoid massive switch-statements.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_percepion_cv.py` for dataset export validation.
- **Regression Check**: Verify no performance drop when Dataset Logging is active.

## 6. Phase Completion Criteria
- [ ] `RewardComponent` is updated correctly by the `EnvironmentJudgeSystem`.
- [ ] Teacher Mode generates clean JSONL/HDF5 datasets with state-action pairs.
- [ ] Shadow Mode provides a real-time diff between agent and human actions.

## 7. Execution Logging & Monitoring
- **Logs**: Record teacher session starts and data dump locations in `simulation.log`.
- **Metrics**: Monitor dataset size and agent reward average.

## 8. Developer Experience (DX)
- **MCP Servers**: Use `sequential-thinking` MCP to define reinforcement learning reward structures. Use `filesystem` MCP to manage large simulation datasets.
