from abc import ABC, abstractmethod
from typing import Any
from serpentine.core.world import World

class System(ABC):
    """
    Abstract base class for all systems.
    Systems contain logic that operates on components.

    Attributes:
        tick_rate (Optional[int]): Target TPS for this system. If None, runs every frame.
        _accumulator (float): Internal time accumulator for tick rate logic.
    """

    def __init__(self, tick_rate: int = None):
        self.tick_rate = tick_rate
        self._accumulator = 0.0

    @abstractmethod
    async def update(self, world: World, dt: float) -> None:
        """
        Updates the system logic.

        Args:
            world: The ECS World instance containing all entities and components.
            dt: Delta time since the last frame (in seconds).
        """
        pass

    def reset(self, world: World) -> None:
        """
        Resets the system's internal state.
        Called during environment resets (e.g. Gym).
        Default implementation clears the accumulator.
        """
        self._accumulator = 0.0
