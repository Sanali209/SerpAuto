# Unified Registry & Node Graph Architecture

This document defines the architecture for the next generation of the Serpentine Engine's metadata, selection, and graph-editing systems.

## 1. Unified Registry System (Registry V2)

The `Registry` will evolve from a simple class map to a metadata-rich discovery service.

### Metadata-Driven Registration
All registerable objects (Components, Systems, BT Nodes, Perception Nodes) will use a unified decorator pattern.

```python
@register_node(category="Logic", icon="🔀", description="Runs children in sequence.")
class SequenceNode(BehaviorTreeNode):
    ...
```

### Registry Categories
- **COMPONENT**: Data structures attached to entities.
- **SYSTEM**: Logic loops processing components.
- **PERCEPTION_NODE**: DAG nodes for CV/Web pipelines.
- **BEHAVIOR_NODE**: Nodes for behavior tree logic.
- **ACTION**: Leaf nodes that execute environment commands.

## 2. Global Selection Service

A central service to synchronize what the user is currently "looking at" across different UI windows.

### Selection Types
- **ENTITY**: Selection of a world entity (UUID).
- **NODE**: Selection of a node within a graph (BT or Perception).
- **COMPONENT**: Selection of a specific component instance for focused editing.

### Selection Propagation (Observer Pattern)
The `SelectionService` broadcasts changes via the `GUIEventBus`.
- **Outliner click** -> Set Entity selection -> **Inspector** refreshes.
- **Node Graph click** -> Set Node selection -> **Inspector** refreshes with node parameters.

## 3. Node Graph Framework

A reusable foundation for visual editors (Perception DAG and Behavior Trees).

### BaseNodeGraphManager (Strategy Pattern)
Abstracts the DPG `add_node_editor` logic.
- **BTGraphManager**: Handles BT specific logic (one root, hierarchical).
- **PipelineGraphManager**: Handles Perception DAG logic (multi-input, directed).

### Parameter Auto-Generation
The Inspector will query the `SelectionService`. If a **Node** is selected:
1. Get the node's Pydantic `params` model.
2. Feed it to `AutoUIBuilder`.
3. Bind changes back to the node instance live.

## 4. Behavior Tree Visualization (Debugging)

### Live Execution Tracking
Nodes will have a `last_status` and `last_tick_time` field.
- **BT Visualizer** queries these fields per tick.
- Nodes are colored based on status:
  - 🟢 **SUCCESS**
  - 🔴 **FAILURE**
  - 🔵 **RUNNING**
  - ⚪ **IDLE**

### BT Debugging Protocol
The Engine (Mind Phase) will provide a `get_bt_snapshot(agent_id)` method, returning the full tree structure with current status overlays.

## Target Structure

```text
core/
├── registry_v2.py      # Metadata-rich registry
└── selection.py        # SelectionService

systems/gui/
└── graph/
    ├── base_graph.py   # Abstract DPG graph handler
    ├── bt_editor.py    # Behavior Tree visual editor
    └── perc_editor.py  # Perception Pipeline visual editor
```

## Benefits
- **Full Extensibility**: Adding a new AI node automatically populates the Visual BT Editor sidebar.
- **Consistent UX**: Parameters are edited in the same Inspector window whether it's a component or a node.
- **Visual Debugging**: Makes opaque LLM and BT logic visible and interactive.
