import logging
from typing import List, Type, Any

from serpentine.modes.base import ModeStrategy
from serpentine.core.registry import Registry, EngineMode, SystemPhase

logger = logging.getLogger(__name__)

class ProductionMode(ModeStrategy):
    """
    Production mode: Headless + Optimized systems + FastAPI bridge.
    Ensures strict separation from GUI and Debug tools.
    """
    def __init__(self):
        super().__init__(EngineMode.PRODUCTION)

    def get_systems(self, phase: SystemPhase) -> List[Type[Any]]:
        # Retrieve all systems registered for PRODUCTION
        systems = Registry.get_systems_for_phase(phase, self.mode)

        filtered_systems = []
        for system_cls in systems:
            # 1. Exclude systems in 'serpentine.systems.gui' package
            if 'serpentine.systems.gui' in system_cls.__module__:
                logger.warning(f"ProductionMode: Excluding GUI system {system_cls.__name__} (found in GUI package)")
                continue

            # 2. Exclude systems that might rely on dearpygui if not explicitly handled
            # (Though most should be in gui package or handle ImportError)
            # We trust the Registry metadata generally, but the package check is a strong safety net.

            filtered_systems.append(system_cls)

        return filtered_systems
