# Phase 8: Operation Modes Guide

This guide covers the specialized execution modes of the Serpentine Engine.

## 1. Objectives
- **Dynamic Config**: Swap systems and tick rates based on usage context.
- **Headless**: Run in high-performance clouds or local servers.
- **Training**: Optimized for RL and SL data flows.

## 2. Technical Prerequisites & Architecture
- [**Architect Mode**](../architect_mode.md)
- [**Production Mode**](../production_mode.md)

## 3. Implementation Status

### 8.1 Core Modes
- [ ] **Architect**: GUI + Full inspection + Dev TPS.
- [ ] **Production**: Headless + Optimized systems + FastAPI bridge.
- [ ] **Gymnasium**: Uncapped TPS + Reward systems + Reset hooks.
- [ ] **Teacher**: Performance metrics + Recording + Human Input.

### 8.2 Engine Lifecycle
- [ ] **CLI Entry**: `main.py` mode switching.
- [ ] **System Filtering**: Automatic exclusion of GUI systems in Production.

### 🛠️ Web Insights & Advanced Patterns
> [!TIP]
> **Strategy Pattern**: Implement engine modes using the Strategy Pattern—each mode (Architect, Production) should be a class that defines its own "System Injection Map." This prevents "Spaghetti if-statements" in the core engine loop.
> - **GameInstance Logic**: Separate per-layer rules (GameMode) from globally persistent data (GameInstance). This ensures that agent scores or memory persist even when switching between different simulation "levels" or environments.

### 🔄 Consolidation Hook: Event-Driven Orchestration
- **Goal**: Remove hardcoded mode-to-system mapping in `main.py`.
- **Action**: Use `RegistryV2` to dynamically load system graphs and feature sets based on the selected mode's metadata, ensuring the engine remains modular.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 7 backlog: `des_docs/planning/backlogs/phase_07_backlog.md`.
- **Output**: Save remaining mode orchestration tasks and technical debt to: `des_docs/planning/backlogs/phase_08_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Each `EngineMode` implementation should reside in its own file within a `modes/` package.
- **Complexity**: Keep `main.py` under 200 lines by delegating all mode-specific setup to the registry and mode strategy classes.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `python main.py --mode PRODUCTION --test-health`.
- **Regression Check**: Verify that `ArchitectMode` overhead does not seep into `ProductionMode` (zero DPG calls in headless).

## 6. Phase Completion Criteria
- [ ] Engine switches modes via CLI without restart.
- [ ] `FastAPI` system exposes full `World` state in Production.
- [ ] Telemetry correctly reports TPS/Memory usage in all modes.

## 7. Execution Logging & Monitoring
- **Logs**: Track mode transitions and system filtering results in `engine.log` via **Loguru**.
- **Metrics**: Monitor `EngineMode` uptime and resource consumption using **Rich.Panel** visuals in the terminal.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `sequential-thinking`: Define and refine system exclusion rules for new modes.
    - `filesystem`: Audit and manage mode-specific configuration files.
