from typing import Any, Callable, Dict, List

class EventBus:
    """
    Simple event bus for decoupling components.
    """
    _subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    @classmethod
    def subscribe(cls, event_type: str, callback: Callable[[Any], None]):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)

    @classmethod
    def publish(cls, event_type: str, data: Any = None):
        if event_type in cls._subscribers:
            for callback in cls._subscribers[event_type]:
                callback(data)

# Alias for backward compatibility if needed, but we should use EventBus generally.
# For now, let's keep GUIEventBus as an alias to avoid breaking too much code,
# or just update the import in `gui/base.py`.
GUIEventBus = EventBus
