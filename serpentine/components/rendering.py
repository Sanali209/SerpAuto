from typing import List, Optional
try:
    from pydantic import Field
except ImportError:
    from serpentine.utils.pydantic_utils import Field

from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry

@Registry.register_component
class CameraComponent(BaseComponent):
    """
    Component defining a camera.
    """
    fov: float = 60.0
    near: float = 0.1
    far: float = 1000.0
    is_orthographic: bool = False
    ortho_size: float = 10.0
    aspect_ratio: float = 1.33

@Registry.register_component
class MeshComponent(BaseComponent):
    """
    Component defining a mesh to render.
    """
    mesh_path: Optional[str] = None
    primitive_type: str = "cube"  # cube, sphere, quad
    color: List[float] = Field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])

@Registry.register_component
class MaterialComponent(BaseComponent):
    """
    Component defining material properties.
    """
    shader_name: str = "default"
    texture_path: Optional[str] = None
    color: List[float] = Field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])
