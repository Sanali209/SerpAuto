import asyncio
import time
import json
import gzip
import traceback
from typing import List, Dict, Type, Any

from serpentine.core.world import World
from serpentine.core.registry import Registry, EngineMode, SystemPhase
from serpentine.systems.base import System
from serpentine.utils.logging import configure_logging
from serpentine.core.event_bus import GUIEventBus
from serpentine.modes import ArchitectMode, ProductionMode, GymnasiumMode, TeacherMode, ModeStrategy
from serpentine.modes.config_loader import ModeConfigLoader

logger = configure_logging()

class SerpentineEngine:
    def __init__(self, mode: EngineMode = EngineMode.ARCHITECT, target_tps: int = 60, config_path: str = None):
        self.mode = mode
        self.mode_config = ModeConfigLoader.load_config(config_path) if config_path else {}
        self._mode_strategy: ModeStrategy = self._create_mode_strategy(mode)
        self.world = World()
        self.is_running = False
        self.paused = False
        self._step_requested = False
        self.target_tps = target_tps
        self.target_tick_time = 1.0 / target_tps
        self.actual_tps = 0.0

        # Subscribe to GUI events
        GUIEventBus.subscribe("ENGINE_PLAY", lambda _: self.play())
        GUIEventBus.subscribe("ENGINE_PAUSE", lambda _: self.pause())
        GUIEventBus.subscribe("ENGINE_STEP", lambda _: self.step())
        GUIEventBus.subscribe("ENGINE_SET_TPS", lambda tps: self.set_tps(tps))
        GUIEventBus.subscribe("ENGINE_SAVE_SNAPSHOT", lambda path: self.save_snapshot(path))
        GUIEventBus.subscribe("ENGINE_LOAD_SNAPSHOT", lambda path: self.load_snapshot(path))
        GUIEventBus.subscribe("ENGINE_TOGGLE_SYSTEM", lambda data: self.toggle_system(data.get("name"), data.get("enabled")))

        # Instantiate systems for this mode
        self.systems: Dict[SystemPhase, List[System]] = {}
        self._initialize_systems()

    def _create_mode_strategy(self, mode: EngineMode) -> ModeStrategy:
        mode_map = {
            EngineMode.ARCHITECT: ArchitectMode,
            EngineMode.PRODUCTION: ProductionMode,
            EngineMode.GYMNASIUM: GymnasiumMode,
            EngineMode.TEACHER: TeacherMode,
        }
        strategy_cls = mode_map.get(mode, ArchitectMode)
        logger.info(f"Using mode strategy: {strategy_cls.__name__}")
        return strategy_cls()

    def play(self):
        self.paused = False
        logger.info("Engine resumed.")

    def pause(self):
        self.paused = True
        logger.info("Engine paused.")

    def step(self):
        self.paused = True
        self._step_requested = True
        logger.info("Engine step requested.")

    def set_tps(self, tps: int):
        self.target_tps = max(1, tps)
        self.target_tick_time = 1.0 / self.target_tps
        logger.info(f"Engine TPS set to {self.target_tps}")

    def save_snapshot(self, filepath: str):
        if not filepath:
            logger.warning("Save snapshot called with empty filepath.")
            return

        try:
            snapshot = self.world.take_snapshot()

            if filepath.endswith('.gz'):
                with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                    json.dump(snapshot, f)
            else:
                with open(filepath, 'w') as f:
                    json.dump(snapshot, f, indent=2)

            logger.info(f"Snapshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save snapshot to {filepath}: {e}")
            traceback.print_exc()

    def load_snapshot(self, filepath: str):
        if not filepath:
            logger.warning("Load snapshot called with empty filepath.")
            return

        try:
            if filepath.endswith('.gz'):
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    snapshot = json.load(f)
            else:
                with open(filepath, 'r') as f:
                    snapshot = json.load(f)

            self.world.restore_snapshot(snapshot)
            logger.info(f"Snapshot loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load snapshot from {filepath}: {e}")
            traceback.print_exc()

    def toggle_system(self, system_name: str, enabled: bool):
        """
        Dynamically enables or disables a system by name.
        Note: This currently works by tracking an internal excluded set or modifying the mode_config.
        Since systems are already instantiated, we need a way to skip them in the loop.
        """
        if not system_name:
            return

        logger.info(f"Toggling system {system_name} to {enabled}")

        # We'll use self.mode_config["excluded_systems"] as the source of truth for dynamic runtime exclusions too.
        excluded = self.mode_config.setdefault("excluded_systems", [])

        if enabled:
            if system_name in excluded:
                excluded.remove(system_name)
        else:
            if system_name not in excluded:
                excluded.append(system_name)

    def _initialize_systems(self):
        """Initializes systems based on the current engine mode."""
        logger.info(f"Initializing engine in {self.mode} mode using {self._mode_strategy.__class__.__name__}...")

        for phase in SystemPhase:
            system_classes = self._mode_strategy.get_systems(phase)
            initialized_systems = []

            # Check exclusions from mode config (for initial instantiation skipping)
            # However, for dynamic toggling, we should instantiate everything and check enabled state in the loop?
            # Or we stick to the current design: "excluded" means "not instantiated".
            # The user asked for "Dynamic System Toggling".
            # If we don't instantiate it, we can't enable it later without re-initializing.

            # Revised approach: Instantiate ALL systems for the mode, but check exclusion list in _tick loop.

            for cls in system_classes:
                # We instantiate regardless of exclusion config, so we can toggle later.
                # UNLESS the mode strategy strictly forbids it? No, Strategy returns list of classes.

                metadata = Registry._system_metadata.get(cls.__name__)
                tick_rate = metadata.tick_rate if metadata else None

                # Override tick_rate from config if present
                if "tick_rates" in self.mode_config and cls.__name__ in self.mode_config["tick_rates"]:
                    tick_rate = self.mode_config["tick_rates"][cls.__name__]

                # Instantiate with tick_rate if the system supports it in __init__
                # Our base System now supports it.
                system = cls()
                if tick_rate:
                    system.tick_rate = tick_rate
                    logger.debug(f"System {cls.__name__} configured with {tick_rate} TPS")

                initialized_systems.append(system)

            self.systems[phase] = initialized_systems
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

        # Reset step request if this is the step frame
        if self._step_requested:
            # We will run all systems this frame
            pass

        # Execute phases in order
        for phase in SystemPhase:
            # Check if we should skip this phase due to pause
            if self.paused and not self._step_requested:
                # Always run TELEMETRY (GUI) and INPUT when paused
                if phase not in [SystemPhase.TELEMETRY, SystemPhase.INPUT]:
                    continue

            systems = self.systems.get(phase, [])
            excluded_systems = self.mode_config.get("excluded_systems", [])

            for system in systems:
                if system.__class__.__name__ in excluded_systems:
                    continue

                try:
                    if system.tick_rate:
                        system._accumulator += dt
                        target_dt = 1.0 / system.tick_rate

                        # If enough time accumulated, run one or more updates
                        # Fixed timestep logic for specific systems
                        if system._accumulator >= target_dt:
                            # Avoid spiral of death by capping max updates?
                            # For simplicity, just run once per tick if ready, consuming accumulated time.
                            # Or run multiple times?
                            # Let's run as many times as needed to catch up, but with a limit?
                            # Simple approach: while accumulator > target_dt: update(target_dt)

                            while system._accumulator >= target_dt:
                                await system.update(self.world, target_dt)
                                system._accumulator -= target_dt
                    else:
                        # Standard system: run every frame with variable dt
                        await system.update(self.world, dt)

                except Exception as e:
                    logger.error(f"Error in system {system.__class__.__name__}: {e}")
                    # Decide whether to crash or continue. Continuing is safer for dev.

        # After completing the tick, clear the step request
        if self._step_requested:
            self._step_requested = False

    def stop(self):
        self.is_running = False
