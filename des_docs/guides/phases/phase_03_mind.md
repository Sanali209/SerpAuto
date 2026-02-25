# Phase 3: Cognitive System (Mind) Guide

This guide covers the behavior tree and AI integration layers.

## 1. Objectives
- **Behavior Tree**: Hierarchical decision-making engine.
- **Blackboard**: Shared memory for agent context.
- **AI Adapters**: Interface for LLM-driven reasoning.

## 2. Technical Prerequisites & Architecture
- [**Behavior Tree Guide**](../BEHAVIOR_TREE_GUIDE.md)
- [**LLM Inference Design**](../../architecture/behavior_tree_editor.md)

## 3. Implementation Status

### 3.1 BT Engine
- [ ] **Core Logic**: `Sequence`, `Selector`, `Inverter`, `Succeeder`.
- [ ] **Status Flow**: `SUCCESS`, `FAILURE`, `RUNNING` propagation.
- [ ] **Parallel Node**: (Pending) Multi-threaded child execution.

### 3.2 AI & Memory
- [ ] **MemoryComponent**: Blackboard key-value storage.
- [ ] **Adapter Interface**: Generic AI provider abstraction.
- [ ] **LLMInferenceNode**: Async node for context-aware reasoning.
- [ ] **External Workflow**: (Pending) N8N and Microservice adapters.

### 🛠️ Web Insights & Advanced Patterns
> [!NOTE]
> **Conditional Aborts**: Optimize BT traversals by using conditional aborts—only re-evaluate logic branches when specific blackboard keys change, rather than ticking the whole tree every frame.
> - **Action Masking**: In LLM/RL agents, use action masking to filter out invalid logical paths before inference, reducing hallucinations and improving decision quality.
> - **Hybrid AI**: Use State Machines for high-level goal switching and Behavior Trees for fine-grained task execution.

### 🔄 Consolidation Hook: Unified Dataflow (Intents)
- **Goal**: Decouple logic from physical execution.
- **Action**: All Behavior Tree action nodes must produce `Intent` objects rather than direct physical commands, allowing the `ActionExecutionSystem` to handle environmental translation.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 2 backlog: `des_docs/planning/backlogs/phase_02_backlog.md`.
- **Output**: Save remaining cognitive tasks and technical debt to: `des_docs/planning/backlogs/phase_03_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Split large Behavior Trees into smaller, reusable sub-trees (Sub-BTs) handled by separate classes if necessary.
- **Complexity**: Use standard BT node patterns to avoid monolithic decision blocks.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_mind_bt.py`.
- **Regression Check**: Validate that BT traversal depth does not impact tick rate. Ensure no memory leaks in the Blackboard.

## 6. Phase Completion Criteria
- [ ] BT leaf nodes successfully emit `Intent` objects.
- [ ] Blackboard supports selective reactivity (observers on keys).
- [ ] `LLMInferenceNode` handles async timeouts and fallback logic.

## 7. Execution Logging & Monitoring
- **Logs**: Track BT status transitions in `mind.log` using **Loguru** for JSON-compatible event logs.
- **Metrics**: Monitor LLM token usage and inference latency per agent via Telemetry.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `sequential-thinking`: Design complex Behavior Tree logic.
    - `filesystem`: Audit large BT JSON blueprints for structure.
