import asyncio
import time
from typing import List, Dict, Optional
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

class EngineMode(Enum):
    ARCHITECT = auto()   # GUI, Debug, Slow
    PRODUCTION = auto()  # Headless, Fast, Telemetry
    TEACHER = auto()     # Human Input, No Brain, Logging
    GYMNASIUM = auto()   # Internal Physics, Rewards, No Sleep

class SerpentineEngineV2(SerpentineEngine):
    """
    Enhanced engine loop with strict phase ordering (v2.0) and Operation Modes.
    """
    def __init__(self, mode: EngineMode = EngineMode.ARCHITECT):
        super().__init__()
        self.mode = mode
        self.systems_by_phase: Dict[Phase, List[System]] = {
            phase: [] for phase in Phase
        }
        self.configure_for_mode()

    def configure_for_mode(self):
        """Sets internal flags based on the selected mode."""
        if self.mode == EngineMode.GYMNASIUM:
            self.tick_rate = 0 # Uncapped
        elif self.mode == EngineMode.PRODUCTION:
            self.tick_rate = 20 # Efficient
        elif self.mode == EngineMode.TEACHER:
            self.tick_rate = 60 # Real-time
        else: # ARCHITECT
            self.tick_rate = 60

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
            # In Gymnasium Mode, we skip sleep to maximize TPS
            if self.mode != EngineMode.GYMNASIUM and self.tick_rate > 0:
                elapsed = time.perf_counter() - current_time
                sleep_time = max(0, (1.0 / self.tick_rate) - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            else:
                # Still yield control to event loop to allow async tasks to progress
                await asyncio.sleep(0)
