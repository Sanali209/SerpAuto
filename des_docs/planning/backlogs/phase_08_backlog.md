# Phase 8: Modes Backlog

This document tracks pending tasks and future improvements for the Engine Modes and Orchestration.

## From Phase 7 (Persistence)
- [x] **Dataset Replay**: Ability to replay a recorded session in the engine. (Relevant to Persistence)
- [ ] **HDF5 Support**: Implement binary format support for large datasets (currently only JSONL is supported).
- [ ] **Generic Router Implementation**: Dynamic environment targeting beyond simple simulation.
- [ ] **Shadow Mode Implementation**: Real-time AI loss monitoring.
- [ ] **Advanced HumanInputSystem**: Mouse mapping and complex input schemes.
- [ ] **EnvironmentJudgeSystem Logic**: Implement actual game rules.
- [ ] **Dataset Validation**: Create `dataset_prep.py`.
- [ ] **Multi-Agent Teacher Mode**: Support controlling multiple agents.

## Phase 8 Specific Tasks
- [ ] **Registry V2**: Implement dynamic loading of system graphs based on configuration files rather than just metadata decorators.
- [ ] **GameInstance Separation**: Separate global persistent data (GameInstance) from per-level rules (GameMode).
- [ ] **FastAPI Bridge**: Expose full `World` state in Production mode via REST/WebSocket.
- [ ] **Telemetry Dashboard**: Enhance `TelemetrySystem` to support Prometheus/Grafana export.
- [ ] **Mode Configuration Files**: Allow defining mode parameters (like system exclusions) in JSON/YAML config files instead of hardcoded Python classes.
- [ ] **Gymnasium Reset Logic**: Implement efficient environment reset without full engine restart.
