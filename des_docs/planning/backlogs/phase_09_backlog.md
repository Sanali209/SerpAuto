# Phase 9: Snake Demo Backlog

This document tracks pending tasks and future improvements for the Snake AI Demo and RL integration.

## Remaining Implementation Tasks
- [x] **Demo Entry Point**: Create `snake_demo.py` to run the game with visualization.
- [x] **Visualization**: Implement a `SnakeRenderSystem` or use `GUIDebugSystem` to visualize the grid state using DearPyGui.
- [x] **Human Input**: Map WASD keys to `ChangeDirectionIntent` in `HumanInputSystem` or a new `SnakeInputSystem` for manual play.
- [ ] **RL Training Script**: Create a script to train a PPO/A2C agent using `stable-baselines3` and `SerpentineGymEnv`.

## Optimization & Refactoring
- [ ] **Gym Reset Optimization**: Currently `reset()` clears the entire world. Optimize to reuse entities or just reset components to improve training speed.
- [ ] **Food Spawning**: Ensure food doesn't spawn on snake body (currently using `random` with a loop, could be slow if snake is long).
- [ ] **State Representation**: Add more features to `snake_state` (e.g. distance to walls/food) to help RL agent.

## Integration
- [ ] **Shadow Mode**: Implement a mode where AI predicts moves while human plays.
- [ ] **Web Dashboard**: Expose snake game state via WebSocket for web-based visualization.
