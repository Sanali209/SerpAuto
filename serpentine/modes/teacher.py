from typing import List, Type, Any

from serpentine.modes.base import ModeStrategy
from serpentine.core.registry import Registry, EngineMode, SystemPhase

class TeacherMode(ModeStrategy):
    """
    Teacher mode: Performance metrics + Recording + Human Input.
    Used for collecting demonstration data from human experts.
    """
    def __init__(self):
        super().__init__(EngineMode.TEACHER)

    def get_systems(self, phase: SystemPhase) -> List[Type[Any]]:
        return Registry.get_systems_for_phase(phase, self.mode)
