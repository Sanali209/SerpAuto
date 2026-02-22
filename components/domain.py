from typing import List, Dict
from core.component import BaseComponent

class StatsComponent(BaseComponent):
    """Vital statistics"""
    health: float = 100.0
    max_health: float = 100.0
    stamina: float = 100.0
    status_effects: List[str] = [] # ["poisoned", "encumbered"]

class InventoryComponent(BaseComponent):
    """Resource management (loot, parts)"""
    capacity: int = 20
    items: Dict[str, int] = {} # {"wood": 50, "iron_ore": 10}
