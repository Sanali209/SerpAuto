# Phase 10: Scene Management & Backlog

This document tracks pending tasks for Scene Management and carry-over items from Phase 9.

## Scene Management Backlog
- [ ] **Delta Serialization**: Implement "Delta Serialization" for scene transitions to reduce disk footprint and load times.
- [ ] **Dynamic System Toggling**: Update `SceneLoader` and `Engine` to support enabling/disabling systems at runtime via scene files.
- [ ] **Global Configuration**: Implement a `World.config` or similar mechanism to store and apply global scene settings (e.g., gravity, game rules).
- [ ] **Blueprint Standardization**: Use Scene Files as the primary specification for environment and agent archetypes (Blueprints V2).
- [ ] **Scene Transitions**: Implement smooth scene transitions, preserving player state or specific entities across loads.

## Phase 9 Carry-Over (Snake Demo & RL)
### Remaining Implementation Tasks
- [x] **Visualization**: Implement a `SnakeRenderSystem` or use `GUIDebugSystem` to visualize the grid state using DearPyGui.
- [x] **Human Input**: Map WASD keys to `ChangeDirectionIntent` in `HumanInputSystem` or a new `SnakeInputSystem` for manual play.
- [ ] **RL Training Script**: Create a script to train a PPO/A2C agent using `stable-baselines3` and `SerpentineGymEnv`.

### Optimization & Refactoring
- [ ] **Gym Reset Optimization**: Currently `reset()` clears the entire world. Optimize to reuse entities or just reset components to improve training speed.
- [ ] **Food Spawning**: Ensure food doesn't spawn on snake body (currently using `random` with a loop, could be slow if snake is long).
- [ ] **State Representation**: Add more features to `snake_state` (e.g. distance to walls/food) to help RL agent.

### Integration
- [ ] **Shadow Mode**: Implement a mode where AI predicts moves while human plays.
- [ ] **Web Dashboard**: Expose snake game state via WebSocket for web-based visualization.
