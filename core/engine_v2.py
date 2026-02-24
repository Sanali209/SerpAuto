import asyncio
import time
from typing import List, Dict, Optional, Any
from enum import Enum, auto

from core.world import World
from core.system import System
from core.engine import SerpentineEngine

class Phase(Enum):
    INPUT = auto()
    MAIL_ROUTING = auto()
    PERCEPTION = auto()
    INTERNAL_PHYSICS = auto()
    COGNITION = auto()
    EXECUTION = auto()
    REWARD = auto()
    TELEMETRY = auto()

class EngineMode(Enum):
    ARCHITECT = 1   # Full GUI, Debugging, Manual intervention
    PRODUCTION = 2  # Headless, telemetry API only
    GYMNASIUM = 3   # Headless, uncapped tick rate, internal physics only
    TEACHER = 4     # GUI + Human Input System + Dataset Recorder (Imitation Learning)
    ACTOR_LEARNER = 5 # Production + Environment Judge + Replay Buffer (Online RL)
    PLAY = 6        # Standalone Game Mode (ModernGL Rendering)

class EngineState(Enum):
    DEV = auto()
    PLAY = auto()

class SerpentineEngineV2(SerpentineEngine):
    """
    Enhanced engine loop with strict phase ordering (v2.0) and Operation Modes.
    """
    def __init__(self, mode: EngineMode = EngineMode.ARCHITECT):
        super().__init__()
        self.mode = mode
        self.state = EngineState.DEV if mode != EngineMode.PLAY else EngineState.PLAY
        self.systems_by_phase: Dict[Phase, List[System]] = {
            phase: [] for phase in Phase
        }
        self.is_running = False
        self.is_paused = False
        self._do_step = False
        self.configure_for_mode()

    def configure_for_mode(self):
        """Sets internal flags based on the selected mode."""
        if self.mode == EngineMode.GYMNASIUM:
            self.tick_rate = 0 # Uncapped
        elif self.mode == EngineMode.PRODUCTION:
            self.tick_rate = 20 # Efficient
        elif self.mode == EngineMode.TEACHER:
            self.tick_rate = 60 # Real-time
        elif self.mode == EngineMode.PLAY:
            self.tick_rate = 0 # V-Sync limited usually
        else: # ARCHITECT
            self.tick_rate = 60

    def add_system(self, system: System, phase: Phase = Phase.EXECUTION):
        """Register a system to a specific execution phase."""
        self.systems_by_phase[phase].append(system)
        # Keep flat list for legacy compatibility if needed
        self.systems.append(system)

    async def run(self):
        self.is_running = True
        self.is_paused = False
        self._do_step = False
        last_time = time.perf_counter()

        # Defined execution order for v2.0
        phase_order = [
            Phase.INPUT,
            Phase.MAIL_ROUTING,
            Phase.PERCEPTION,
            Phase.INTERNAL_PHYSICS,
            Phase.COGNITION,
            Phase.EXECUTION,
            Phase.REWARD,
            Phase.TELEMETRY
        ]

        while self.is_running:
            current_time = time.perf_counter()
            dt = current_time - last_time
            last_time = current_time

            if not self.is_paused or self._do_step:
                # Execute phases in strict order
                for phase in phase_order:
                    for system in self.systems_by_phase[phase]:
                        await system.update(self.world, dt)
                
                self._do_step = False

            # Artificial delay (Sleep)
            # In Gymnasium Mode, we skip sleep to maximize TPS
            if self.mode != EngineMode.GYMNASIUM and self.tick_rate > 0:
                elapsed = time.perf_counter() - current_time
                sleep_time = max(0, (1.0 / self.tick_rate) - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            else:
                # Still yield control to event loop to allow async tasks to progress
                await asyncio.sleep(0.001) # Small sleep to prevent CPU hogging in while loop

    async def update_once(self, dt: float):
        """Execute one full update cycle (all phases)."""
        phase_order = [
            Phase.INPUT,
            Phase.MAIL_ROUTING,
            Phase.PERCEPTION,
            Phase.INTERNAL_PHYSICS,
            Phase.COGNITION,
            Phase.EXECUTION,
            Phase.REWARD,
            Phase.TELEMETRY
        ]
        for phase in phase_order:
            for system in self.systems_by_phase[phase]:
                await system.update(self.world, dt)
