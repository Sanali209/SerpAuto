from typing import Type, Dict, Optional
from core.component import BaseComponent
from core.system import System
from core.engine_v2 import Phase

class Registry:
    """Central registry for Components and Systems."""

    _components: Dict[str, Type[BaseComponent]] = {}
    _systems: Dict[str, Type[System]] = {}
    _system_phases: Dict[str, Phase] = {}

    @classmethod
    def register_component(cls):
        """Decorator to register a Component class."""
        def wrapper(component_cls: Type[BaseComponent]):
            cls._components[component_cls.__name__] = component_cls
            return component_cls
        return wrapper

    @classmethod
    def register_system(cls, phase: Phase = Phase.EXECUTION):
        """Decorator to register a System class with a target phase."""
        def wrapper(system_cls: Type[System]):
            cls._systems[system_cls.__name__] = system_cls
            cls._system_phases[system_cls.__name__] = phase
            return system_cls
        return wrapper

    @classmethod
    def get_component(cls, name: str) -> Optional[Type[BaseComponent]]:
        return cls._components.get(name)

    @classmethod
    def get_system(cls, name: str) -> Optional[Type[System]]:
        return cls._systems.get(name)

    @classmethod
    def get_system_phase(cls, name: str) -> Phase:
        return cls._system_phases.get(name, Phase.EXECUTION)

    @classmethod
    def get_all_components(cls) -> Dict[str, Type[BaseComponent]]:
        return cls._components

# Aliases for easier use
register_component = Registry.register_component
register_system = Registry.register_system
COMPONENT_REGISTRY = Registry._components # Backwards compatibility
