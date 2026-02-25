# Phase XX: [Phase Name] Guide

This guide provides autonomous instructions for implementing Phase XX.

## 1. Objectives
- [Objective 1]
- [Objective 2]

## 2. Technical Prerequisites & References
- [Reference 1](../../path/to/doc.md)
- [Reference 2](../../path/to/doc.md)

## 3. Implementation Steps

### XX.1 [Sub-step Name]
1. [Action]
2. [Action]

### 🛠️ Web Insights & Advanced Patterns
> [!TIP]
> [Modern best practice tip here]

### 🔄 Consolidation Hook: [Pillar Name]
- **Goal**: [Alignment goal]
- **Action**: [Specific refactoring or integration action]

## 4. Backlog Management
- **Input**: Read the pending tasks from the previous phase backlog: `des_docs/planning/backlogs/phase_XX-1_backlog.md` (or `des_docs/planning/tasks.md` for Phase 1).
- **Output**: Save remaining tasks and technical debt to: `des_docs/planning/backlogs/phase_XX_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: If a file grows beyond 500 lines, split it into smaller modules (e.g., `logic.py`, `types.py`, `utils.py`) within a package.
- **Complexity**: Prefer descriptive function names and typed hints to reduce comments.

## 6. Quality Assurance & Testing
- **Automated Tests**: `pytest path/to/tests`
- **Regression Check**: [Specific performance or stability constraint]

## 7. Phase Completion Criteria
- [ ] [Metric or functionality 1]
- [ ] [Metric or functionality 2]

## 8. Execution Logging & Monitoring
- **Logs**: Monitor `[file].log` for `[Module]` events.
- **Metrics**: Track `[Metric Name]` in Telemetry.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `sequential-thinking`: Mandatory for complex logic/BT design.
    - `filesystem`: Auditing file length limits and package structures.
    - `document-index`: Context-aware documentation retrieval.
