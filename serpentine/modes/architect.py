from typing import List, Type, Any

from serpentine.modes.base import ModeStrategy
from serpentine.core.registry import Registry, EngineMode, SystemPhase

class ArchitectMode(ModeStrategy):
    """
    Architect mode: GUI + Full inspection + Dev TPS.
    This mode includes all registered systems for ARCHITECT.
    """
    def __init__(self):
        super().__init__(EngineMode.ARCHITECT)

    def get_systems(self, phase: SystemPhase) -> List[Type[Any]]:
        # Use Registry's default behavior, filtering for ARCHITECT mode
        return Registry.get_systems_for_phase(phase, self.mode)
