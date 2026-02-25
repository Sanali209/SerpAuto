# Phase 5: God Mode (Developer UI) Guide

This guide covers the DearPyGui-based development workspace and visual debugging tools.

## 1. Objectives
- **Workspace**: Professional docking layout and control center.
- **Inspection**: Real-time entity and component mutation.
- **Visualization**: GPU-backed viewports and data trees.

## 2. Technical Prerequisites & Architecture
- [**Auto UI Builder Architecture**](../../architecture/auto_ui_builder.md)
- [**GUI Modernization Plan**](../../architecture/gui_modernization_design.md)

## 3. Implementation Status

### 5.1 Core Workspace
- [ ] **GUIDebugSystem**: Main DPG context and viewport setup.
- [ ] **Control Deck**: Transport controls (Play/Pause/Step/TPS).
- [ ] **Time Travel UI**: (In Progress) Snapshot restoration buttons.

### 5.2 Outliner & Inspector
- [ ] **World Outliner**: Hierarchical entity list with CRUD.
- [ ] **Component Inspector**: Dynamic property editing via `AutoUIBuilder`.
- [ ] **Registry Integration**: Dropdown for adding components from the registry.

### 🛠️ Web Insights & Advanced Patterns
> [!TIP]
> **Responsive DPG**: Achieving responsiveness in DearPyGui requires implementing window-resize callbacks to programmatically adjust `child_window` dimensions.
> - **Docking Space**: Set `docking=True` and `docking_space=True` in `dpg.configure_app` to enable professional IDE-like window snapping.
> - **Visual Hierarchy**: Use `dpg.group(horizontal=True)` with `indent` and `spacer` parameters to create scanning paths that guide the developer's eye during deep debugging sessions.

### 🔄 Consolidation Hook: Global Selection Service
- **Goal**: Synchronize user focus across all visual tools.
- **Action**: Implement the `SelectionService` to ensure that selecting an entity in the Outliner, a node in the Graph, or a message in the Sniffer focuses the Inspector and Telemetry panels.

### 5.3 Specialized Monitors
- [ ] **Perception Viewport**: Zero-copy GPU texture rendering.
- [ ] **Blackboard Monitor**: Real-time table view of agent memory.
- [ ] **Action Timeline**: (Pending) Gantt-style execution log.
- [ ] **BT Visual Editor**: (Detailed in Phase 13 Guide).

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 4 backlog: `des_docs/planning/backlogs/phase_04_backlog.md`.
- **Output**: Save remaining UI/debug tasks and technical debt to: `des_docs/planning/backlogs/phase_05_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Break generic UI modules into specialized window classes (e.g., `inspector_window.py`, `outliner_window.py`).
- **Complexity**: Host all DPG layout logic in separate `view` files decoupled from system logic.

## 6. Quality Assurance & Testing
- **Manual Verification**: Verify that clicking entities in the Outliner updates the Inspector.
- **Regression Check**: DPG UI consumption should not exceed 5% CPU in idle Architect Mode.

## 6. Phase Completion Criteria
- [ ] `SelectionService` synchronizes all active windows.
- [ ] `AutoUIBuilder` supports all primitive types and nested dicts.
- [ ] Docking layouts persist between application restarts.

## 7. Execution Logging & Monitoring
- **Logs**: Log UI event bus traffic (e.g., selection changes) in `gui.log` at the `DEBUG` level.
- **Metrics**: Track UI FPS alongside simulation TPS in the Control Deck.

## 8. Developer Experience (DX)
- **MCP Servers**: Use `filesystem` MCP to manage DPG layout files. Use `sequential-thinking` MCP to plan the migration of legacy GUI code.
