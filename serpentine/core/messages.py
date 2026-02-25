from typing import Any, Dict, Optional
try:
    from pydantic import BaseModel, Field
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, Field
from uuid import UUID
import time

from serpentine.core.entity import EntityID

class SwarmMessage(BaseModel):
    """
    Standard message format for inter-agent communication.
    """
    sender_id: EntityID
    recipient_id: Optional[EntityID] = None  # None implies broadcast
    topic: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    ttl: float = 5.0  # Time to live in seconds
