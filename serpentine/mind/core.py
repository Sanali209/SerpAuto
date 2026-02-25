from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

try:
    from pydantic import BaseModel, Field
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, Field

class Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"

class Blackboard(BaseModel):
    """
    Shared memory for the Behavior Tree.
    """
    data: Dict[str, Any] = Field(default_factory=dict)

    def set(self, key: str, value: Any):
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def has(self, key: str) -> bool:
        return key in self.data

    def clear(self):
        self.data.clear()

class BehaviorTreeNode(ABC):
    """
    Base class for all Behavior Tree nodes.
    """
    class Params(BaseModel):
        pass

    def __init__(self, params: Optional[BaseModel] = None):
        self.params = params or self.Params()
        self.status: Status = Status.FAILURE

    @abstractmethod
    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        """
        Executes the node logic.
        Must return a Status enum.
        """
        pass

    def reset(self):
        """
        Resets the node state. Override if the node holds internal state (like RUNNING tasks).
        """
        self.status = Status.FAILURE
