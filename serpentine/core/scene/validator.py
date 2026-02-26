from typing import Dict, List, Any, Optional
try:
    from pydantic import BaseModel, Field
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, Field # type: ignore

class SceneMetadata(BaseModel):
    """Metadata for a scene file."""
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    created_at: Optional[str] = None
    author: Optional[str] = None

class SystemConfig(BaseModel):
    """Configuration for a system within a scene."""
    name: str
    enabled: bool = True
    priority_override: Optional[int] = None
    tick_rate_override: Optional[int] = None
    config: Dict[str, Any] = Field(default_factory=dict)

class EntityData(BaseModel):
    """Serialized data for a single entity."""
    uid: str
    components: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class SceneData(BaseModel):
    """Top-level structure for a scene file."""
    metadata: SceneMetadata
    systems: List[SystemConfig] = Field(default_factory=list)
    entities: List[EntityData] = Field(default_factory=list)
    global_config: Dict[str, Any] = Field(default_factory=dict)
