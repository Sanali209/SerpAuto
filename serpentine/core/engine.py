import asyncio
import time
from typing import List, Dict, Type

from serpentine.core.world import World
from serpentine.core.registry import Registry, EngineMode, SystemPhase
from serpentine.systems.base import System
from serpentine.utils.logging import configure_logging

logger = configure_logging()

class SerpentineEngine:
    def __init__(self, mode: EngineMode = EngineMode.ARCHITECT, target_tps: int = 60):
        self.mode = mode
        self.world = World()
        self.is_running = False
        self.target_tps = target_tps
        self.target_tick_time = 1.0 / target_tps
        self.actual_tps = 0.0

        # Instantiate systems for this mode
        self.systems: Dict[SystemPhase, List[System]] = {}
        self._initialize_systems()

    def _initialize_systems(self):
        """Initializes systems based on the current engine mode."""
        logger.info(f"Initializing engine in {self.mode} mode...")

        for phase in SystemPhase:
            system_classes = Registry.get_systems_for_phase(phase, self.mode)
            self.systems[phase] = [cls() for cls in system_classes]
            logger.debug(f"Phase {phase.name}: {[s.__class__.__name__ for s in self.systems[phase]]}")

    async def run(self):
        """Main engine loop."""
        self.is_running = True
        logger.info("Engine started.")

        last_time = time.time()

        try:
            while self.is_running:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                # Update TPS counter (simple moving average or instant)
                if dt > 0:
                    self.actual_tps = 1.0 / dt

                await self._tick(dt)

                # Sleep to maintain target TPS
                elapsed = time.time() - current_time
                sleep_time = max(0, self.target_tick_time - elapsed)

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

        except asyncio.CancelledError:
            logger.info("Engine loop cancelled.")
        finally:
            self.is_running = False
            logger.info("Engine stopped.")

    async def _tick(self, dt: float):
        """Executes one tick of the engine loop."""
        # Execute phases in order
        # We iterate over SystemPhase enum to ensure order
        for phase in SystemPhase:
            systems = self.systems.get(phase, [])
            for system in systems:
                try:
                    await system.update(self.world, dt)
                except Exception as e:
                    logger.error(f"Error in system {system.__class__.__name__}: {e}")
                    # Decide whether to crash or continue. Continuing is safer for dev.
                    # In production, maybe crash? For now, log and continue.

    def stop(self):
        self.is_running = False
