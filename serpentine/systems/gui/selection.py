from typing import Any, Optional
from serpentine.systems.gui.base import GUIEventBus

class SelectionService:
    """
    Singleton service to manage global selection state across GUI windows.
    """
    _selected_item: Optional[Any] = None
    _selected_type: Optional[str] = None

    @classmethod
    def set_selected(cls, item: Any, item_type: str):
        """
        Sets the currently selected item and notifies listeners.

        Args:
            item: The object being selected (e.g., Entity ID, Component, Node).
            item_type: A string identifier for the type of item (e.g., "ENTITY", "NODE").
        """
        if cls._selected_item != item:
            cls._selected_item = item
            cls._selected_type = item_type
            GUIEventBus.publish("SELECTION_CHANGED", {"item": item, "type": item_type})

    @classmethod
    def get_selected(cls) -> Optional[Any]:
        return cls._selected_item

    @classmethod
    def get_selected_type(cls) -> Optional[str]:
        return cls._selected_type

    @classmethod
    def clear_selection(cls):
        cls.set_selected(None, None)
