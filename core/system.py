from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.world import World

class BaseSystem(ABC):
    """Base class for all ECS systems."""

    @abstractmethod
    async def update(self, world: "World", dt: float):
        """Update logic for the system.

        Args:
            world: The game world instance.
            dt: Delta time since last frame.
        """
        pass
