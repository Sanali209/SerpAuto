# Auto UI Builder

The `AutoUIBuilder` (`systems/auto_ui_builder.py`) is a powerful introspection tool that dynamically generates **DearPyGui (DPG)** widgets from **Pydantic** models.

## 🚀 Overview

This system allows for "Zero-Code UI" generation. If you define a new component as a Pydantic model, the `AutoUIBuilder` can automatically create an inspector panel for it with **Live Data Binding**.

## 🛠️ Supported Types

The builder recursively traverses Pydantic fields and maps them to DPG elements:

| Pydantic Type | DPG Widget | Behavior |
| :--- | :--- | :--- |
| `str` | `add_input_text` | Real-time text edit |
| `int` / `float` | `add_drag_int/float` | Slider/Input with step |
| `bool` | `add_checkbox` | Toggle switch |
| `Enum` | `add_combo` | Dropdown selection |
| `BaseModel` | `add_tree_node` | Recursive nested UI |
| `Dict` / `List` | `add_tree_node` | Grouped views with heuristic editing |

## 🔗 Live Binding

The builder creates closure-based callbacks that automatically update the underlying Pydantic model instance when the UI widget is modified.

```python
# Example Usage in a System
def create_inspector(self, entity_id):
    comp = world.get_component(entity_id, MyComponent)
    AutoUIBuilder.build_ui_for_model(comp, parent_tag="InspectorPanel")
```

---

## 🔧 Exclusion & Customization

- **Exclusion**: Fields marked with `exclude=True` in the Pydantic field definition (e.g., `Field(exclude=True)`) will be ignored by the builder.
- **Internal Fields**: Fields prefixed with `_` are skipped by default.

> [!TIP]
> Use `exclude=True` for large numpy arrays or sensitive buffers (like `processed_frame` in `PerceptionComponent`) to prevent UI lag.
