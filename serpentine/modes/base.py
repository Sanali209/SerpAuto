from abc import ABC, abstractmethod
from typing import List, Type, Any

from serpentine.core.registry import Registry, EngineMode, SystemPhase

class ModeStrategy(ABC):
    """
    Abstract base class for engine execution mode strategies.
    Each mode defines its own system injection map and configuration.
    """
    def __init__(self, mode: EngineMode):
        self.mode = mode

    @abstractmethod
    def get_systems(self, phase: SystemPhase) -> List[Type[Any]]:
        """
        Returns a list of system classes for the given phase.
        The default implementation queries the Registry, but subclasses
        can override this to enforce strict filtering or custom injection.
        """
        pass
