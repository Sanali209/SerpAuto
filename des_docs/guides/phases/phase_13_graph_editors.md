# Phase 13: Visual Graph Editors Guide

This guide covers the implementation of visual designers for agent logic (Behavior Trees) and perception pipelines.

## 1. Objectives
- **BT Visual Editor**: High-fidelity node graph for designing agent "brains" with live status highlighting.
- **Perception Editor**: DAG visualizer for CV/Web data flows.
- **No-Code Integration**: Drag-and-drop node instantiation from the Registry.

## 2. Technical Prerequisites & References
- [**Behavior Tree Visual Editor Design**](../../architecture/behavior_tree_editor.md)
- [**Unified Registry & Selection**](../../architecture/unified_registry_and_node_graph.md)
- [**Behavior Tree Guide**](../BEHAVIOR_TREE_GUIDE.md)

## 3. Implementation Steps

### 13.1 Behavior Tree Editor (`systems/gui/graph/bt_editor/`)
1.  **Canvas Setup**:
    - Use DPG's `add_node_editor`.
    - Implement `link_callback` to validate BT logic (e.g., prevent cycles, ensure one parent per node).
2.  **Node Registry Sync**:
    - Populate the sidebar by querying `RegistryV2` for nodes in the "Behavior" and "Action" categories.
    - Map DPG node creation to `BehaviorTreeNode` subclasses.
3.  **Live Debugging**:
    - Implement `DebuggingManager` to poll the active agent's BT status per tick.
    - Change node background colors in the DPG canvas: 🟢 Success, 🔴 Failure, 🔵 Running.
4.  **Inspector Persistence**:
    - Bind the Editor to the `SelectionService`.
    - Ensure selecting a node in the graph triggers the Inspector to render its Pydantic parameters.

### 13.2 Perception Pipeline Editor
1.  **DAG Visualization**:
    - Visualize existing `PerceptionPipelineSystem` configurations.
    - Add "Preview Pins" that show a small thumbnail of the data- [ ] **Execution Highlight**: Visual glow on the currently active BT node.

### 🛠️ Web Insights & Advanced Patterns
> [!NOTE]
> **Graph UX Best Practices**: 
> - **Auto-Layout**: Integrate a Sugiyama-style layout algorithm to clean up messy graphs with one click.
> - **Mini-map**: For complex Behavior Trees, provide a "Birds-eye view" mini-map corner to help users navigate between deep sub-trees.
> - **Execution Heatmaps**: Color-code node connections based on "tick frequency" to visually identify performance bottlenecks or logic loops in real-time.

### 🔄 Consolidation Hook: Generic Visual Graph UX
- **Goal**: Extract 90% of graph logic into a reusable base class for the entire engine.
- **Action**: Implement generic zooming, panning, selection, and serialization in `BaseNodeCanvas` to be inherited by the Behavior Tree Editor, Perception Pipeline Editor, and future logic tools.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 12 backlog: `des_docs/planning/backlogs/phase_12_backlog.md`.
- **Output**: Save remaining graph editor tasks and technical debt to: `des_docs/planning/backlogs/phase_13_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Extract `BaseNodeCanvas` into a package: `canvas/base.py`, `canvas/links.py`, `canvas/serialization.py`.
- **Complexity**: Keep node types in separate registration files to avoid a single massive "nodes" module.

## 6. Quality Assurance & Testing
- **Manual Verification**: Create a complex BT and verify all node status highlights update in real-time.
- **Regression Check**: Ensure that large graphs (50+ nodes) do not cause UI stuttering during panning/zooming.

## 6. Phase Completion Criteria
- [ ] `BaseNodeCanvas` supports zooming, panning, and selection.
- [ ] BT Editor correctly highlights active nodes (Success/Fail/Running).
- [ ] Perception Editor correctly visualizes DAG flows and previews pins.

## 7. Execution Logging & Monitoring
- **Logs**: Log all graph link/unlink events and serialization failures in `graph_editors.log`.
- **Metrics**: Monitor graph rendering overhead in DPG.

## 8. Developer Experience (DX)
- **MCP Servers**: Use `sequential-thinking` MCP to design the auto-layout algorithm. Use `filesystem` MCP to manage graph blueprint files.
