from typing import List, Dict, Any, Optional, Tuple
try:
    from pydantic import Field, BaseModel
except ImportError:
    from serpentine.utils.pydantic_utils import Field, BaseModel
from uuid import UUID

from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry
from serpentine.perception.types import Observation
from serpentine.mind.intent import Intent

@Registry.register_component
class PerceptionComponent(BaseComponent):
    """
    Stores short-term sensory observations from perception nodes.
    Acts as the interface between Perception and Cognition systems.
    """
    observations: Dict[str, Observation] = Field(default_factory=dict)
    # Stores the latest processed frames or data for debugging/logging
    debug_data: Dict[str, Any] = Field(default_factory=dict)

    def add_observation(self, key: str, observation: Observation):
        self.observations[key] = observation

    def get_observation(self, key: str) -> Optional[Observation]:
        return self.observations.get(key)


@Registry.register_component
class ActionBufferComponent(BaseComponent):
    """
    Queue for pending actions (Intents) to be executed by the ActionExecutionSystem.
    """
    action_queue: List[Intent] = Field(default_factory=list)
    shadow_queue: List[Intent] = Field(default_factory=list)
    history: List[Tuple[float, Intent]] = Field(default_factory=list)
    last_executed_intent: Optional[Intent] = None

    def enqueue(self, action: Intent):
        self.action_queue.append(action)

    def enqueue_shadow(self, action: Intent):
        self.shadow_queue.append(action)

    def dequeue(self) -> Optional[Intent]:
        if self.action_queue:
            return self.action_queue.pop(0)
        return None

    def clear(self):
        self.action_queue.clear()
        self.shadow_queue.clear()
