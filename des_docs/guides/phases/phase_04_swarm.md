# Phase 4: Multi-Agent System (Swarm) Guide

This guide covers inter-agent communication and coordinated swarm intelligence.

## 1. Objectives
- **Identity**: Unique agent metadata and roles.
- **Messaging**: Pub/Sub architecture for decentralized control.
- **Monitoring**: Real-time traffic sniffer for debugging.

## 2. Technical Prerequisites & Architecture
- [**Routing System**](../../architecture/ARCHITECTURE.md#phase-4-internal-routing--swarm)
- [**Swarm Monitoring Design**](../../architecture/gui_modernization_design.md)

## 3. Implementation Status

### 4.1 Agent Identity & Messaging
- [ ] **AgentMetaComponent**: Roles, status, and naming.
- [ ] **MailboxComponent**: Decoupled inbox/outbox storage.
- [ ] **Message Model**: Typed Pydantic messages for swarm traffic.

### 4.2 Swarm Orchestration
- [ ] **MessageRouterSystem**: Global bus logic for routing packets.
- [ ] **BT Nodes**: `SendMessageNode`, `ListenForEventNode`.
- [ ] **Mailbox Persistence**: (Pending) Save/Load of long-term message logs.
- [ ] **Message Sniffer UI**: (Integrated in future GUI phases).

### 🛠️ Web Insights & Advanced Patterns
> [!TIP]
> **Pub/Sub vs Blackboard**: Use Pub/Sub for transient events (e.g., "Ally Spotted") and Blackboard for persistent shared state (e.g., "Global Enemy Count").
> - **Backpressure**: Implement message TTL (Time-To-Live) and Dead-Letter Queues to prevent slow agents from clogging the global message router.
> - **Idempotency**: Ensure that critical swarm actions are idempotent, as decentralized networks can occasionally double-fire events during high synchronization load.

### 🔄 Consolidation Hook: Plugin Architecture (Unified Event Bus)
- **Goal**: Unify internal and external event handling.
- **Action**: Merge the `MessageRouterSystem` into the `UnifiedEngineEventBus` to support seamless communication between core systems and future external plugins.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 3 backlog: `des_docs/planning/backlogs/phase_03_backlog.md`.
- **Output**: Save remaining swarm/routing tasks and technical debt to: `des_docs/planning/backlogs/phase_04_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Separate routing logic from agent mailbox components to keep system modules manageable.
- **Complexity**: Ensure message schemas are kept in separate, concise Pydantic model files.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_swarm.py`.
- **Regression Check**: Track packet loss in high-congestion scenarios. Message latency must remain < 10ms for local routing.

## 6. Phase Completion Criteria
- [ ] `MessageRouterSystem` successfully delivers 1k messages/sec.
- [ ] Agents can respond to `ListenForEventNode` within 2 ticks.
- [ ] Swarm identities are persistent across world snapshots.

## 7. Execution Logging & Monitoring
- **Logs**: Record all inter-agent traffic in `swarm.log` via **Loguru** (toggleable).
- **Metrics**: Monitor `MailboxComponent` queue depth and packet loss.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `sequential-thinking`: Model multi-agent communication protocols.
    - `web-search`: Research common MAS architectural pitfalls.
