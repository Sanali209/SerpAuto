import asyncio
from typing import Optional, Any, Dict
try:
    import numpy as np
except ImportError:
    np = None

try:
    import mss
except ImportError:
    mss = None

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.perception.components import PerceptionComponent
from serpentine.perception.types import Observation

@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.ARCHITECT, EngineMode.TEACHER, EngineMode.PRODUCTION])
class SensoryInputSystem(System):
    """
    Ingests raw sensory data (Screen) and stores it in the PerceptionComponent.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)
        self.sct = mss.mss() if mss else None
        # Default monitor 1 or fallback
        if self.sct and len(self.sct.monitors) > 1:
            self.monitor = self.sct.monitors[1]
        else:
            self.monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

    async def update(self, world: World, dt: float) -> None:
        entities = world.get_components(PerceptionComponent)
        if not entities:
            return

        # Capture screen once per frame
        raw_image = self.capture_screen()

        observation = Observation(
            source_node="SensoryInputSystem",
            data_type="image",
            content=raw_image,
            metadata={"width": self.monitor["width"], "height": self.monitor["height"], "channels": 4 if self.sct else 3}
        )

        # Distribute to all entities with PerceptionComponent
        # TODO: Filter by entity needs/config
        for entity_id, perception in entities.items():
            perception.add_observation("raw_screen", observation)

    def capture_screen(self):
        if self.sct and np:
            sct_img = self.sct.grab(self.monitor)
            # mss returns BGRA, we keep it as is for now, or convert if needed
            return np.array(sct_img)
        elif np:
            # Return dummy black image if mss not available
            return np.zeros((self.monitor["height"], self.monitor["width"], 3), dtype=np.uint8)
        else:
            return None


@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.GYMNASIUM])
class InternalStateReaderSystem(System):
    """
    Ingests internal simulation state directly for Gymnasium/RL training.
    """
    async def update(self, world: World, dt: float) -> None:
        entities = world.get_components(PerceptionComponent)
        if not entities:
            return

        # In a real internal sim, we would query other components (e.g. Grid, Snake)
        # For now, we emit a placeholder 'internal_state' observation

        state_data = {
            "entity_count": len(world.entities),
            "dt": dt
        }

        observation = Observation(
            source_node="InternalStateReaderSystem",
            data_type="internal_state",
            content=state_data,
            metadata={}
        )

        for entity_id, perception in entities.items():
            perception.add_observation("raw_internal", observation)
