from typing import Dict, Any, Optional
from pydantic import Field
from components.base import BaseComponent

class TransformComponent(BaseComponent):
    """Physical position on screen or world."""
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

class VelocityComponent(BaseComponent):
    """Velocity vector for physics."""
    vx: float = 0.0
    vy: float = 0.0

class ColliderComponent(BaseComponent):
    """Collider for collision detection."""
    is_solid: bool = True
    layer: str = "default"

class DOMNodeComponent(BaseComponent):
    """HTML element snapshot."""
    xpath: str = ""
    css_selector: str = ""
    attributes: Dict[str, str] = Field(default_factory=dict)
    extracted_text: str = ""

class PayloadExtractionComponent(BaseComponent):
    """Container for extracted data."""
    target_schema_name: str = ""
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    validation_status: bool = False

class UIElementComponent(BaseComponent):
    """UI element semantics."""
    element_type: str = "button"
    is_interactable: bool = True
