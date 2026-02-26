from typing import Tuple
try:
    from pydantic import Field
except ImportError:
    from serpentine.utils.pydantic_utils import Field

from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry

@Registry.register_component
class ColliderComponent(BaseComponent):
    """
    Component defining a physics collider.
    """
    shape: str = "box"  # box, sphere
    # For box: (width, height, depth)
    size: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    # For sphere: (radius, 0, 0)
    radius: float = 0.5
    offset: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    is_trigger: bool = False
