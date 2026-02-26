# Phase 7: Persistence Backlog

This document tracks pending tasks and future improvements for the Persistence Layer and State Management.

## From Phase 6 (Simulation & Teacher Mode)
- [x] **Dataset Replay**: Ability to replay a recorded session in the engine. (Relevant to Persistence)
- [ ] **HDF5 Support**: Implement binary format support for large datasets (currently only JSONL is supported).
- [ ] **Generic Router Implementation**: Dynamic environment targeting beyond simple simulation.
- [ ] **Shadow Mode Implementation**: Real-time AI loss monitoring.
- [ ] **Advanced HumanInputSystem**: Mouse mapping and complex input schemes.
- [ ] **EnvironmentJudgeSystem Logic**: Implement actual game rules.
- [ ] **Dataset Validation**: Create `dataset_prep.py`.
- [ ] **Multi-Agent Teacher Mode**: Support controlling multiple agents.

## Phase 7 Specific Tasks
- [ ] **Protobuf Support**: Implement Protocol Buffers for high-performance state serialization (10-20x faster than JSON).
- [ ] **Deterministic Replay**: Ensure RNG seeding is serialized in snapshots for perfect reproduction.
- [ ] **Blueprints System**: Implement reusable configurations for Behavior Trees and Perception DAGs (beyond basic loading).
- [ ] **Registry Versioning**: Handle schema migrations for components when loading old snapshots.
- [x] **Auto-Save**: Implement periodic auto-saves during simulation.
- [x] **Snapshot Compression**: Use GZIP or similar for JSON snapshots to reduce disk usage.
