from abc import ABC, abstractmethod
from typing import Any
from serpentine.core.world import World

class System(ABC):
    """
    Abstract base class for all systems.
    Systems contain logic that operates on components.
    """

    @abstractmethod
    async def update(self, world: World, dt: float) -> None:
        """
        Updates the system logic.

        Args:
            world: The ECS World instance containing all entities and components.
            dt: Delta time since the last frame (in seconds).
        """
        pass
