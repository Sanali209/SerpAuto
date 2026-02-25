# Node Parameter Standards

To maintain consistency and enable automatic UI/documentation generation, all nodes in the Serpentine Engine (Perception, Cognition, etc.) must follow these standards for parameter management.

## 1. Use Pydantic Models
Every node should have a corresponding Pydantic `BaseModel` to define its parameters.

```python
from pydantic import BaseModel, Field

class MyNodeParams(BaseModel):
    speed: float = Field(1.0, description="How fast the node processes.")
    mode: str = Field("FAST", description="Processing mode.")
```

## 2. Constructor Pattern
Nodes should accept parameters as keyword arguments and initialize their internal `params` object.

```python
class MyNode:
    def __init__(self, **kwargs):
        self.params = MyNodeParams(**kwargs)
```

## 3. Parameter Access
Access parameters through `self.params` during the `process` or `update` methods.

```python
def process(self, data):
    if self.params.mode == "FAST":
        # ...
```

## 4. Documentation
Always include a `description` in the `Field` definition. This description is used for automatic UI tooltips and documentation generation.

## 5. UI Integration
By using Pydantic, the `model_json_schema()` method can be used to automatically generate UI forms in the Architect GUI.
