import asyncio
import time
from typing import List, Dict
from enum import Enum, auto

from core.world import World
from core.system import System
from core.engine import SerpentineEngine

class Phase(Enum):
    MAIL_ROUTING = auto()
    PERCEPTION = auto()
    INTERNAL_PHYSICS = auto()
    COGNITION = auto()
    EXECUTION = auto()
    TELEMETRY = auto()

class SerpentineEngineV2(SerpentineEngine):
    """
    Enhanced engine loop with strict phase ordering (v2.0).
    """
    def __init__(self):
        super().__init__()
        self.systems_by_phase: Dict[Phase, List[System]] = {
            phase: [] for phase in Phase
        }

    def add_system(self, system: System, phase: Phase = Phase.EXECUTION):
        """Register a system to a specific execution phase."""
        self.systems_by_phase[phase].append(system)
        # Keep flat list for legacy compatibility if needed
        self.systems.append(system)

    async def run(self):
        self.is_running = True
        last_time = time.perf_counter()

        # Defined execution order for v2.0
        phase_order = [
            Phase.MAIL_ROUTING,
            Phase.PERCEPTION,
            Phase.INTERNAL_PHYSICS,
            Phase.COGNITION,
            Phase.EXECUTION,
            Phase.TELEMETRY
        ]

        while self.is_running:
            current_time = time.perf_counter()
            dt = current_time - last_time
            last_time = current_time

            # Execute phases in strict order
            for phase in phase_order:
                for system in self.systems_by_phase[phase]:
                    await system.update(self.world, dt)

            # Artificial delay (Sleep)
            elapsed = time.perf_counter() - current_time
            sleep_time = max(0, (1.0 / self.tick_rate) - elapsed)
            await asyncio.sleep(sleep_time)
