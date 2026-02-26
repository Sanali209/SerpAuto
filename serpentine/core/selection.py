from typing import Any, Optional
from serpentine.core.event_bus import GUIEventBus

class SelectionService:
    """
    Singleton service to manage global selection state across GUI windows.
    """
    _selected_item: Optional[Any] = None
    _selected_type: Optional[str] = None

    @classmethod
    def set_selected(cls, item: Any, item_type: Optional[str]):
        """
        Sets the currently selected item and notifies listeners.

        Args:
            item: The object being selected (e.g., Entity ID, Component, Node).
            item_type: A string identifier for the type of item (e.g., "ENTITY", "NODE", "COMPONENT").
        """
        if cls._selected_item != item or cls._selected_type != item_type:
            cls._selected_item = item
            cls._selected_type = item_type
            GUIEventBus.publish("ON_SELECTION_CHANGED", {"item": item, "type": item_type})

    @classmethod
    def get_selected(cls) -> Optional[Any]:
        return cls._selected_item

    @classmethod
    def get_selected_type(cls) -> Optional[str]:
        return cls._selected_type

    @classmethod
    def clear_selection(cls):
        cls.set_selected(None, None)
