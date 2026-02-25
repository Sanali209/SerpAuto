# Perception Pipeline Visual Editor Design

The Perception Pipeline Editor is a visual tool for designing, testing, and debugging the engine's data ingestion DAG (Directed Acyclic Graph). It allows developers to chain CV and Web nodes into complex processing pipelines that emit a standardized `Observation`.

## 1. Core Visual Framework

The editor is built upon the engine's consolidated **Graph Foundation**.

- **Canvas Foundation**: Inherits from `BaseNodeCanvas`, providing universal panning, zooming, and node selection logic.
- **Node Engine**: Uses DearPyGui's `add_node_editor`.
- **DAG Enforcement**: Unlike the Behavior Tree (which is hierarchical), this editor strictly enforces a Directed Acyclic Graph structure, preventing loops in data processing.

## 2. Metadata-Driven Discovery (Registry V2)

The editor sidebar is automatically populated using the engine's unified registration system.

- **`@register_node` Categories**: Nodes are filtered by `category="Perception"`.
- **Dynamic Pins**: The editor inspects the node class to determine input/output pins based on the data type (e.g., `ImageLink`, `DOMNodeLink`).

```python
@register_node(category="Perception", icon="📸", description="Crops an incoming image.")
class CropNode(PerceptionNode):
    class Params(BaseModel):
        x: int = 0
        y: int = 0
        w: int = 100
        h: int = 100
```

## 3. The Dataflow: Raw to Observation

The editor visualizes the data transformation pipeline defined in the [**Dataflow Architecture**](dataflow_architecture.md).

1.  **Ingestion Nodes**: (e.g., `ScreenCaptureNode`) Capture raw environment data.
2.  **Processing Nodes**: (e.g., `YOLONode`, `OCRNode`) Transform pixels into structured abstractions.
3.  **Terminal Node (The Sink)**: Every valid pipeline must end in a node that populates the `ObservationComponent`.

## 4. Selection & Live Inspector

The editor leverages the **Unified Selection Service** for real-time parameter tuning.

- **Node Selection**: Clicking a node sets `SelectionService.set_node_selection(node_id)`.
- **AutoUI Binding**: The **Inspector** receives the event and uses `AutoUIBuilder` to render the node's Pydantic `Params`.
- **Live Feed (Preview)**: Hovering over a link between nodes displays a pop-up thumbnail of the data crossing that link (e.g., the cropped image or the detected bounding boxes).

## 5. Persistence & Blueprints

- **Pipeline JSON**: Full graph topology and node parameters are serialized as a project blueprint.
- **Hot-Reloading**: Changes in the editor can be "Committed" to update the active `PerceptionPipelineSystem` without restarting the engine.

## Target Structure

```text
systems/gui/graph/
├── base_graph.py    # Common canvas logic
└── perc_editor.py   # Perception-specific DAG logic
```
