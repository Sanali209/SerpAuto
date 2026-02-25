# Phase 14: Analytics & Swarm Monitoring Guide

This guide details the construction of multi-agent monitoring tools and behavioral analytics.

## 1. Objectives
- **Global Swarm Roster**: A high-level dashboard for tracking dozens of agents simultaneously.
- **Action Execution Timeline**: A Gantt-style visualization of agent intents and actions over time.
- **Imitation Learning Monitor**: Real-time evaluation of AI prediction accuracy in Shadow Mode.

## 2. Technical Prerequisites & References
- [**Modernized Debug UI Architecture**](../../architecture/gui_modernization_design.md)
- [**Teacher Mode & Continuous Learning**](../../modes/actor_learner.md)

## 3. Implementation Steps

### 14.1 Global Swarm Roster (`systems/gui/windows/roster.py`)
1.  **Table Overview**:
    - Create a DPG table showing Agent ID, Tag, Current BT Status, and FPS.
    - Add a "Focus" button to each row that updates the `SelectionService` to target that agent.
2.  **Resource Tracking**:
    - Integrate with `StatsComponent` to show real-time health/stamina/CPU usage per agent.

### 14.2 Action Execution Timeline (`systems/gui/windows/timeline.py`)
1.  **Horizontal Visualization**:
    - Track the history of executed actions in the `ActionExecutionSystem`.
    - Render a scrolling timeline where each action is a block with a duration.
    - Color-code actions by type (e.g., Movement=Blue, Combat=Red).

### 14.3 Imitation Learning Monitor
1.  **Shadow Mode Diffs**:
    - Create a window that compares the human's input (Teacher Mode) with the AI's "Shadow" prediction.
    - Render a real-time loss graph using DPG's `add_plot`.
    - [ ] **InfluxDB/Prometheus**: (Pending) Export adapter for external dashboards.

### 🛠️ Web Insights & Advanced Patterns
> [!IMPORTANT]
> **Blended Telemetry**: A swarm dashboard should monitor both "Infra Health" (CPU/RAM/API Latency) and "Behavioral Drift" (e.g., agents getting stuck in loops).
> - **Token Economy Tracking**: For LLM-driven agents, provide real-time "Cost-per-Action" metrics and hard-kill triggers for tokens to prevent runaway loops from draining API credits.
> - **OpenTelemetry**: Standardize on OTel for tracing agent handoffs; this allows exporting logs to world-class tools like Grafana for complex swarm post-mortems.

### 🔄 Consolidation Hook: Unified Dataflow (Flow Monitoring)
- **Goal**: Monitor the health and synchronization of the consolidated data pipeline.
- **Action**: Track the transition latency between Observation, Intent, and Command to identify performance bottlenecks across the swarm or environment bridges.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 13 backlog: `des_docs/planning/backlogs/phase_13_backlog.md`.
- **Output**: Save remaining analytics/monitoring tasks and technical debt to: `des_docs/planning/backlogs/phase_14_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Separate data collection (polling) from visualization (plotting) to prevent UI thread blocking.
- **Complexity**: Use concise, standardized telemetry packets for multi-agent reporting.

## 6. Quality Assurance & Testing
- **Multi-Agent Load**: Spawn 20 agents and verify the Swarm Roster remains responsive.
- **Regression Check**: Ensure analytics background polling does not exceed 1% CPU.

## 6. Phase Completion Criteria
- [ ] Swarm Roster displays real-time health for 20+ agents.
- [ ] Action Execution Timeline shows correct sequences and durations.
- [ ] Imitation Learning Monitor accurately plots real-time loss.

## 7. Execution Logging & Monitoring
- **Logs**: Record significant behavioral drift events and telemetry overflows in `analytics.log` via **Loguru** using JSON serialization for downstream analysis.
- **Metrics**: Track average agent FPS and LLM cost metrics. Display the Global Swarm Roster in the terminal using **Rich.Columns** during long-running headless simulations.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `sequential-thinking`: Define behavioral analytics logic and anomaly thresholds.
    - `web-search`: Discover industry-standard imitation learning visualization patterns.
