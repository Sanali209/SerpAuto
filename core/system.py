from abc import ABC, abstractmethod
from typing import List, Any
from .world import World

class System(ABC):
    @abstractmethod
    async def update(self, world: World, dt: float):
        """Update logic for this system. Must be implemented by subclasses."""
        pass
