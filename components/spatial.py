from typing import List, Optional, Any
import uuid
from pydantic import Field, model_validator
from core.component import BaseComponent
from core.registry import register_component

@register_component()
class HierarchyComponent(BaseComponent):
    """
    Defines parent-child relationships for Data-Driven Hierarchy.
    Allows constructing scene graphs where child transforms are relative to parents.
    """
    parent: Optional[uuid.UUID] = None
    children: List[uuid.UUID] = Field(default_factory=list)

@register_component()
class TransformComponent(BaseComponent):
    """
    Physical position in 2D/3D space.
    If attached to a HierarchyComponent with a parent, (local_x, local_y) are relative.
    The System calculates (world_x, world_y) for rendering/physics.
    """
    # Local coordinates (relative to parent, or world if no parent)
    local_x: float = 0.0
    local_y: float = 0.0
    local_rotation: float = 0.0
    local_scale_x: float = 1.0
    local_scale_y: float = 1.0

    # World coordinates (computed by TransformHierarchySystem)
    world_x: float = 0.0
    world_y: float = 0.0
    world_rotation: float = 0.0
    world_scale_x: float = 1.0
    world_scale_y: float = 1.0

    # Legacy/Flat fields (mapped to World for backward compatibility)
    width: float = 0.0
    height: float = 0.0
    layer: int = 0

    @model_validator(mode='before')
    @classmethod
    def map_legacy_fields(cls, data: Any) -> Any:
        """
        Supports legacy instantiation: TransformComponent(x=100, y=100).
        Maps 'x' -> 'local_x' and 'world_x'.
        """
        if isinstance(data, dict):
            if 'x' in data:
                val = data.pop('x')
                data['local_x'] = val
                data['world_x'] = val
            if 'y' in data:
                val = data.pop('y')
                data['local_y'] = val
                data['world_y'] = val
            if 'rotation' in data:
                val = data.pop('rotation')
                data['local_rotation'] = val
                data['world_rotation'] = val
        return data

    @property
    def x(self) -> float: return self.world_x
    @x.setter
    def x(self, value: float):
        self.world_x = value
        # For root entities, local == world. For children, this setter is dangerous
        # but needed for compatibility. Ideally, move logic to System.
        self.local_x = value

    @property
    def y(self) -> float: return self.world_y
    @y.setter
    def y(self, value: float):
        self.world_y = value
        self.local_y = value

@register_component()
class SpatialGridComponent(BaseComponent):
    """For navigation (A* Pathfinding) in games or complex interfaces"""
    grid_x: int = 0
    grid_y: int = 0
    is_passable: bool = True
    weight: float = 1.0 # 1.0 - road, 5.0 - swamp/difficult terrain

@register_component()
class UIElementComponent(BaseComponent):
    """Semantics of UI element (button, input field, window header)"""
    element_type: str # "button", "input_field", "window_header"
    extracted_text: str | None = None # Text extracted via OCR (Docling/Tesseract)
    is_interactable: bool = True
