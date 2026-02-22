from core.component import BaseComponent
from core.registry import register_component

@register_component()
class TransformComponent(BaseComponent):
    """Physical position on screen or in world"""
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    layer: int = 0 # Useful for overlapping windows or 2D sprites

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
