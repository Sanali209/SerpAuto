from typing import List, Type, Any

from serpentine.modes.base import ModeStrategy
from serpentine.core.registry import Registry, EngineMode, SystemPhase

class GymnasiumMode(ModeStrategy):
    """
    Gymnasium mode: Uncapped TPS + Reward systems + Reset hooks.
    Optimized for Reinforcement Learning training.
    """
    def __init__(self):
        super().__init__(EngineMode.GYMNASIUM)

    def get_systems(self, phase: SystemPhase) -> List[Type[Any]]:
        return Registry.get_systems_for_phase(phase, self.mode)
