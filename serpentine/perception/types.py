from typing import Any, Dict, Optional, Union
try:
    from pydantic import BaseModel, Field
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, Field
from datetime import datetime

class Observation(BaseModel):
    """
    Standardized observation object emitted by all perception nodes.
    Wraps raw data with metadata.
    """
    source_node: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data_type: str  # e.g., 'image', 'text', 'dom', 'grid'
    content: Any    # The actual payload (e.g., np.ndarray, string, dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
