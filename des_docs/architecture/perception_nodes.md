3.  This document lists all available perception nodes. Nodes in the [**Perception Pipeline**](engine_overview.md#3-восприятие-и-компьютерное-зрение-perception-pipeline) process raw inputs into standardized **Observation** objects. These nodes are visually managed in the [**Perception Pipeline Editor**](perception_pipeline_editor.md).

## 1. Registration & Discovery

All nodes must be registered via the `Registry V2` to appear in the visual editor's library.

```python
@register_node(category="Perception", icon="🔍")
class MyNewNode(PerceptionNode):
    ...
```

## 2. Available Nodes

## Framework Nodes

### PerceptionNode
Base class for all perception nodes.
- **Parameters**: None

---

## CV Nodes

### ScreenCaptureNode
Captures the screen using the `mss` library.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `monitor_index` | `int` | `1` | Index of the monitor to capture. 0 for all monitors. |

### CropNode
Crops the input image.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `x` | `int` | `0` | Top-left X coordinate. |
| `y` | `int` | `0` | Top-left Y coordinate. |
| `w` | `int` | `100` | Width of the crop. |
| `h` | `int` | `100` | Height of the crop. |

### GrayscaleNode
Converts the input image to grayscale. No parameters.

### YOLONode
Runs YOLO object detection on the input image.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `model_path` | `str` | `"yolov8n.onnx"` | Path to the ONNX model file. |
| `confidence` | `float` | `0.5` | Confidence threshold for detections. |
