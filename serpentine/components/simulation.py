from typing import Dict, Any
try:
    from pydantic import Field
except ImportError:
    from serpentine.utils.pydantic_utils import Field

from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry

@Registry.register_component
class RewardComponent(BaseComponent):
    """
    Stores reinforcement learning reward signals.
    """
    current_reward: float = 0.0
    cumulative_reward: float = 0.0
    last_action_reward: float = 0.0

@Registry.register_component
class GoalComponent(BaseComponent):
    """
    Tracks the entity's high-level goal and completion status.
    """
    goal_state: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    is_completed: bool = False
    is_failed: bool = False

@Registry.register_component
class DatasetConfigComponent(BaseComponent):
    """
    Configuration for data collection (Teacher Mode).
    """
    dataset_path: str = "simulation_data.jsonl"
    format: str = "jsonl"  # or "hdf5"
    is_recording: bool = False

@Registry.register_component
class InputControlComponent(BaseComponent):
    """
    Tag component indicating this entity can be controlled by human input.
    """
    enabled: bool = True
