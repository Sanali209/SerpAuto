from typing import Type, Dict, List, Optional, Any
try:
    from pydantic import BaseModel
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel

class RegistryMeta(BaseModel):
    category: str
    icon: str
    description: str

class RegistryV2:
    _nodes: Dict[str, Type[Any]] = {}
    _node_metadata: Dict[str, RegistryMeta] = {}

    _systems: Dict[str, Type[Any]] = {}
    _system_metadata: Dict[str, RegistryMeta] = {}

    _windows: Dict[str, Type[Any]] = {}
    _window_metadata: Dict[str, RegistryMeta] = {}

    @classmethod
    def register_node(cls, category: str, icon: str = "🧩", description: str = ""):
        def wrapper(node_cls: Type[Any]) -> Type[Any]:
            cls._nodes[node_cls.__name__] = node_cls
            cls._node_metadata[node_cls.__name__] = RegistryMeta(
                category=category,
                icon=icon,
                description=description
            )
            return node_cls
        return wrapper

    @classmethod
    def register_system(cls, category: str = "System", icon: str = "⚙️", description: str = ""):
        def wrapper(system_cls: Type[Any]) -> Type[Any]:
            cls._systems[system_cls.__name__] = system_cls
            cls._system_metadata[system_cls.__name__] = RegistryMeta(
                category=category,
                icon=icon,
                description=description
            )
            return system_cls
        return wrapper

    @classmethod
    def register_window(cls, category: str = "Window", icon: str = "🪟", description: str = ""):
        def wrapper(window_cls: Type[Any]) -> Type[Any]:
            cls._windows[window_cls.__name__] = window_cls
            cls._window_metadata[window_cls.__name__] = RegistryMeta(
                category=category,
                icon=icon,
                description=description
            )
            return window_cls
        return wrapper

    @classmethod
    def get_nodes_by_category(cls, category: str) -> List[Type[Any]]:
        return [
            cls._nodes[name]
            for name, meta in cls._node_metadata.items()
            if meta.category == category
        ]

    @classmethod
    def get_windows_by_category(cls, category: str) -> List[Type[Any]]:
        return [
            cls._windows[name]
            for name, meta in cls._window_metadata.items()
            if meta.category == category
        ]

    @classmethod
    def get_all_windows(cls) -> List[Type[Any]]:
        return list(cls._windows.values())

    @classmethod
    def get_node_metadata(cls, name: str) -> Optional[RegistryMeta]:
        return cls._node_metadata.get(name)

    @classmethod
    def get_window_metadata(cls, name: str) -> Optional[RegistryMeta]:
        return cls._window_metadata.get(name)

    @classmethod
    def get_system_metadata(cls, name: str) -> Optional[RegistryMeta]:
        return cls._system_metadata.get(name)
