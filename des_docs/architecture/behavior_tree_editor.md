# Behavior Tree Visual Editor Design

The Behavior Tree (BT) Editor is the central tool for designing and debugging agent cognition in the Serpentine Engine. It provides a visual interface to construct complex logic trees and observe their execution in real-time.

## 1. Visual Interface & Interaction

### Node Graph Canvas
- **Engine**: Built using DearPyGui's `add_node_editor`.
- **Nodes**: Each BT node is represented by a DPG node with input/output pins.
- **Drag-and-Drop**: Dragging a node type from the library onto the canvas instantiates a new node.

### Node Library & Attribute-Based Registration
The editor uses the [**Registry V2**](unified_registry_and_node_graph.md#1-unified-registry-system-registry-v2) for automatic node discovery.
- **`@register_node` Attribute**: Developers add a decorator to BT node classes to specify metadata (category, icon, default params).
- **Auto-Population**: The Sidebar scans the registry and generates drag-and-drop tiles for every registered node.

```python
@register_node(category="Actions", icon="🖱️", description="Clicks a web element.")
class ClickNode(BehaviorTreeNode):
    class Params(BaseModel):
        selector: str
        timeout: float = 5.0
    ...
```

### Logic Flow Serialization
- **Save/Load**: Trees are serialized to a structured JSON format that the `BrainComponent` and `BehaviorTree` logic can ingest.
- **Auto-Layout**: "Clean Up" button to organize nodes using a hierarchical layout algorithm.

## 2. Selection & Inspector Integration

The BT Editor leverages the engine's [**Unified Selection Service**](unified_registry_and_node_graph.md#2-global-selection-service) to handle parameter editing.

### The Selection Flow
1.  **User Click**: User clicks a node in the BT Graph.
2.  **Event Broadcast**: The Editor calls `SelectionService.set_node_selection(node_id)`.
3.  **Inspector Redirect**: The [**Inspector Window**](gui_modernization_design.md#integrated-core-systems) receives the `NODE_SELECTED` event via the `GUIEventBus`.
4.  **AutoUI Generation**: The Inspector retrieves the node's `Params` (Pydantic model) and uses the [**AutoUIBuilder**](auto_ui_builder.md) to generate editable fields.
5.  **Live Binding**: Changes in the Inspector are written back to the node instance in the simulation state.

## 3. Live Debugging & Visualization

### Execution Highlighting
The editor subscribes to the engine's tick cycle to visualize the "active" path of logic for the selected agent.
- **Node Coloring**:
  - 🟢 **Success**: Node returned success on the last tick.
  - 🔴 **Failure**: Node returned failure.
  - 🔵 **Running**: Node is currently in an async operation (e.g., LLM inference).
  - ⚪ **Idle**: Node was not visited in the last tick.
- **Link Pulsing**: Links pulse or change color to indicate the direction of the last logic traverse.

### Breakpoints & Stepping
- **Pause on Failure**: Option to auto-pause the engine if a specific node returns failure.
- **Step-by-Tick**: Advance the behavior tree logic one node traversal at a time.

## 3. GUI Integration Layers

### Inspector Synergy
- When a node is clicked in the graph, the **SelectionService** broadcasts the Node Selection.
- The **InspectorWindow** automatically switches to "Node Mode" and uses **AutoUIBuilder** to render the node's Pydantic parameters.
- Changes in the Inspector are immediately reflected in the node instance in the World.

### Blackboard Monitor (The "Mind" View)
- A side-panel or overlay specifically for the selected agent's **MemoryComponent** (Blackboard).
- Real-time table view of keys and values.
- Ability to manually override blackboard variables during a "Running" state for testing edge cases.

## 4. Advanced Features

### Sub-Tree Embedding
- Ability to reference another `.json` BT as a single "Sub-Tree" node, enabling modular and hierarchical AI design.

### Live Hot-Swapping
- Edit a tree while the engine is running and hit "Commit" to hot-swap the agent's brain without resetting the simulation.

## Target structure

```text
systems/gui/graph/
├── bt_editor/
│   ├── canvas.py    # DPG node editor setup and link handling
│   ├── library.py   # Registry-based node sidebar
│   ├── debugging.py # Execution highlighting and status polling
│   └── serial.py    # JSON Import/Export logic
```

## Benefits
- **Opaque to Transparent**: Turns complex, nested logic into a visible, interactive map.
- **Iteration Speed**: drastically reduces the time to prototype new agent behaviors.
- **Verification**: Perfect for checking why an LLM-driven agent chose a specific (potentially incorrect) path.
