# Phase 7: Persistence (Snapshots & Blueprints) Guide

This guide covers the saving, loading, and "time travel" capabilities of the engine.

## 1. Objectives
- **Serialization**: Deep-copy of world state to JSON/Disk.
- **Snapshots**: One-click restore points for debugging.
- **Blueprints**: Reusable configurations for BTs and Perception DAGs.

## 2. Technical Prerequisites & Architecture
- [**Persistence System Architecture**](../../architecture/persistence_system.md)

## 3. Implementation Status

### 7.1 Serialization
- [ ] **World Serialize**: Pydantic-backed component dumping.
- [ ] **Registry Mapping**: Dynamic reconstruction of classes from string names.

### 7.2 Developer Experience
- [ ] **Snapshots**: UI buttons for dumping and loading world state.
- [ ] **Time Travel**: Engine pause-load-resume cycle.
- [ ] **BT/DAG Blueprints**: (Partial) BT loading is implemented, visual save is Phase 13.

### 🛠️ Web Insights & Advanced Patterns
> [!NOTE]
> **Protobuf for State**: While JSON is great for debugging, consider **Protocol Buffers** for production-grade world snapshots. Protobuf is 10-20x faster and produces significantly smaller files, which is critical for "Time Travel" features that store multiple restore points in memory.
> - **Deterministic Replay**: Ensure all random number generators (RNG) in the engine are seeded and their states are serialized within the snapshot to allow for perfect deterministic reproduction of AI bugs.

### 🔄 Consolidation Hook: Centralized State Service
- **Goal**: Move persistence from a standalone system to a core World trait.
- **Action**: Implement `World.take_snapshot()` to allow for instant architectural undo/redo and "time-travel" debugging across the entire engine.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 6 backlog: `des_docs/planning/backlogs/phase_06_backlog.md`.
- **Output**: Save remaining persistence tasks and technical debt to: `des_docs/planning/backlogs/phase_07_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Isolate registry serialization logic from the core `World` snapshotting method.
- **Complexity**: Model all save schemas using concise, validated structure classes to keep parsing files short.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_persistence.py`.
- **Regression Check**: Snapshot size should not grow exponentially with simulation duration (check for leak of stale entities).

## 6. Phase Completion Criteria
- [ ] `World.take_snapshot()` captures 100% of component state.
- [ ] "Time Travel" (Pause-Load-Resume) works without engine desync.
- [ ] Registry permits loading components across different file versions.

## 7. Execution Logging & Monitoring
- **Logs**: Record snapshot save/load durations and file sizes in `persistence.log` via **Loguru**.
- **Metrics**: Monitor `World` serialization time via the engine's built-in Telemetry.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `filesystem`: Audit and manage world snapshot files.
    - `sequential-thinking`: Plan complex database/persistence schema migrations.
