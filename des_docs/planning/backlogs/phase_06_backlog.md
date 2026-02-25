# Phase 6: Simulation Backlog

This document tracks pending tasks and future improvements for the Simulation Layer and Teacher Mode.

## High Priority
- [ ] **Generic Router Implementation**: Dynamic environment targeting beyond simple simulation.
- [ ] **Shadow Mode Implementation**: Real-time AI loss monitoring (running AI in parallel with human input).
- [ ] **Advanced HumanInputSystem**: Implement mouse mapping and more complex input schemes.
- [ ] **HDF5 Support**: Implement binary format support for large datasets (currently only JSONL is supported).

## Medium Priority
- [ ] **EnvironmentJudgeSystem Logic**: Implement actual game rules for reward calculation instead of placeholder.
- [ ] **Dataset Validation**: Create a script `dataset_prep.py` to validate and compile datasets.
- [ ] **Imitation Learning Loss Monitor**: Visualize the difference between human and AI actions in real-time.

## Low Priority
- [ ] **Dataset Replay**: Ability to replay a recorded session in the engine.
- [ ] **Multi-Agent Teacher Mode**: Support controlling multiple agents or switching control.
