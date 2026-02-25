from enum import Enum, auto
from typing import Type, Dict, List, Optional, Any, Set
try:
    from pydantic import BaseModel
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel

from serpentine.core.component import BaseComponent

class EngineMode(str, Enum):
    ARCHITECT = "ARCHITECT"
    PRODUCTION = "PRODUCTION"
    TEACHER = "TEACHER"
    GYMNASIUM = "GYMNASIUM"
    CONTINUOUS_LEARNING = "CONTINUOUS_LEARNING"

class SystemPhase(str, Enum):
    INPUT = "INPUT"
    MAIL_ROUTING = "MAIL_ROUTING"
    PERCEPTION = "PERCEPTION"
    INTERNAL_PHYSICS = "INTERNAL_PHYSICS"
    COGNITION = "COGNITION"
    EXECUTION = "EXECUTION"
    REWARD = "REWARD"
    TELEMETRY = "TELEMETRY"

class SystemMetadata(BaseModel):
    phase: SystemPhase
    modes: List[EngineMode]
    priority: int = 0  # Higher runs first within phase
    tick_rate: Optional[int] = None  # Specific TPS for this system, None = Engine TPS

class Registry:
    _components: Dict[str, Type[BaseComponent]] = {}
    _systems: Dict[str, Type[Any]] = {}  # Type[System] but System is not defined yet
    _system_metadata: Dict[str, SystemMetadata] = {}

    @classmethod
    def register_component(cls, component_cls: Type[BaseComponent]) -> Type[BaseComponent]:
        """Decorator to register a component class."""
        cls._components[component_cls.__name__] = component_cls
        return component_cls

    @classmethod
    def register_system(cls, phase: SystemPhase, modes: Optional[List[EngineMode]] = None, priority: int = 0, tick_rate: Optional[int] = None):
        """
        Decorator to register a system class with metadata.

        Args:
            phase: The engine phase this system runs in.
            modes: List of modes where this system is active. None = All modes.
            priority: Execution order within phase (Higher = First).
            tick_rate: Custom update rate (TPS) for this system. If None, runs every engine tick.
        """
        if modes is None:
            modes = list(EngineMode)

        def wrapper(system_cls: Type[Any]) -> Type[Any]:
            cls._systems[system_cls.__name__] = system_cls
            cls._system_metadata[system_cls.__name__] = SystemMetadata(
                phase=phase,
                modes=modes,
                priority=priority,
                tick_rate=tick_rate
            )
            return system_cls
        return wrapper

    @classmethod
    def get_component(cls, name: str) -> Optional[Type[BaseComponent]]:
        return cls._components.get(name)

    @classmethod
    def get_all_components(cls) -> Dict[str, Type[BaseComponent]]:
        return cls._components.copy()

    @classmethod
    def get_systems_for_phase(cls, phase: SystemPhase, mode: EngineMode) -> List[Type[Any]]:
        """Returns a list of system classes for a specific phase and mode, sorted by priority."""
        systems = []
        for name, metadata in cls._system_metadata.items():
            if metadata.phase == phase and mode in metadata.modes:
                systems.append((cls._systems[name], metadata.priority))

        # Sort by priority (descending)
        systems.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in systems]

    @classmethod
    def get_all_systems(cls) -> Dict[str, Type[Any]]:
        return cls._systems.copy()
