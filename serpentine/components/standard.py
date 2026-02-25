from typing import Optional, List
try:
    from pydantic import Field
except ImportError:
    from serpentine.utils.pydantic_utils import Field
from uuid import UUID

from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry
from serpentine.core.entity import EntityID

@Registry.register_component
class TransformComponent(BaseComponent):
    """
    Stores position, rotation, and hierarchy information.
    """
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0

    # Hierarchy
    parent: Optional[EntityID] = None
    children: List[EntityID] = Field(default_factory=list)

@Registry.register_component
class StatsComponent(BaseComponent):
    """
    Generic stats for game entities.
    """
    health: float = 100.0
    max_health: float = 100.0
    stamina: float = 100.0
    max_stamina: float = 100.0
    is_alive: bool = True
