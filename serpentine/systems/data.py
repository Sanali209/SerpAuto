import json
import logging
from typing import Optional, Dict, Any
import os
import time
from datetime import datetime
from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.components.simulation import DatasetConfigComponent, RewardComponent
from serpentine.perception.components import ActionBufferComponent
from serpentine.components.standard import TransformComponent
from serpentine.core.event_bus import GUIEventBus
from uuid import UUID

logger = logging.getLogger(__name__)

@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.ARCHITECT])
class DatasetReplaySystem(System):
    """
    Replays a dataset file by applying recorded actions/states to entities.
    Configure via World.config['replay']:
        dataset_path: str
        enabled: bool
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)
        self.file_handle = None
        self.dataset_path = None
        self.finished = False

    async def update(self, world: World, dt: float) -> None:
        config = world.config.get("replay", {})
        if not config.get("enabled", False):
            return

        path = config.get("dataset_path")
        if not path or not os.path.exists(path):
            return

        if self.dataset_path != path:
            # New dataset
            if self.file_handle:
                self.file_handle.close()
            try:
                self.file_handle = open(path, 'r')
                self.dataset_path = path
                self.finished = False
                logger.info(f"Started replaying dataset: {path}")
            except Exception as e:
                logger.error(f"Failed to open replay dataset: {e}")
                return

        if self.finished or not self.file_handle:
            return

        try:
            line = self.file_handle.readline()
            if not line:
                self.finished = True
                logger.info("Replay finished.")
                return

            entry = json.loads(line)

            # Apply state/action
            # In a real replay, we might need to sync time or wait
            # For now, we apply one step per tick

            entity_id_str = entry.get("entity_id")
            if not entity_id_str:
                return

            # Attempt to find entity.
            # Note: IDs might not match if we didn't restore a snapshot first!
            # Assuming we are replaying on top of the correct initial state.

            # TODO: Handle ID mapping if needed. For now assume UUID matches.

            # Apply Transform
            state = entry.get("state")
            if state:
                # We need to find the entity. World stores by ID but we only have string.
                # Ineffecient search?
                # Actually world._components keys are EntityID (UUID).
                try:
                    target_uuid = UUID(entity_id_str)
                    # We can't easily check existence without iterating or try/catch on get_component?
                    # get_component handles it.

                    # Create a dummy EntityID wrapper if needed, but UUID should work for lookup if key is UUID
                    # Python dict lookup with UUID object works.

                    # Wait, EntityID is NewType('EntityID', UUID).

                    transform = world.get_component(target_uuid, TransformComponent)
                    if transform:
                        transform.x = state.get("x", transform.x)
                        transform.y = state.get("y", transform.y)
                        transform.rotation = state.get("rotation", transform.rotation)

                except ValueError:
                    pass

        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"Error during replay: {e}")

@Registry.register_system(phase=SystemPhase.TELEMETRY, modes=[EngineMode.TEACHER, EngineMode.ARCHITECT])
class AutoSaveSystem(System):
    """
    Periodically saves the world state to an autosave file.
    Configuration via World.config['autosave']:
        enabled: bool (default True)
        interval: float (seconds, default 300)
        max_saves: int (default 5)
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)
        self.last_save_time = time.time()
        self.save_index = 0

    async def update(self, world: World, dt: float) -> None:
        config = world.config.get("autosave", {})
        enabled = config.get("enabled", True)
        if not enabled:
            return

        interval = config.get("interval", 300.0) # 5 minutes default
        current_time = time.time()

        if current_time - self.last_save_time >= interval:
            self.last_save_time = current_time
            self.perform_autosave(world, config)

    def perform_autosave(self, world: World, config: Dict[str, Any]):
        try:
            autosave_dir = "autosaves"
            if not os.path.exists(autosave_dir):
                os.makedirs(autosave_dir)

            max_saves = config.get("max_saves", 5)
            filename = f"autosave_{self.save_index}.json"
            filepath = os.path.join(autosave_dir, filename)

            # Use EventBus to request save, decoupled from engine instance
            GUIEventBus.publish("ENGINE_SAVE_SNAPSHOT", filepath)

            logger.info(f"Auto-save triggered: {filepath}")

            self.save_index = (self.save_index + 1) % max_saves
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")


@Registry.register_system(phase=SystemPhase.TELEMETRY, modes=[EngineMode.TEACHER, EngineMode.GYMNASIUM])
class DatasetLoggerSystem(System):
    """
    Logs state-action pairs to a dataset file.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)
        self.file_handles: Dict[str, Any] = {}

    async def update(self, world: World, dt: float) -> None:
        entities = world.get_entities_with(DatasetConfigComponent)
        active_paths = set()

        for entity_id, config in entities:
            if not config.is_recording:
                continue

            path = config.dataset_path
            active_paths.add(path)

            # Ensure file is open
            if path not in self.file_handles:
                try:
                    self.file_handles[path] = open(path, "a")
                except Exception as e:
                    logger.error(f"Failed to open dataset file {path}: {e}")
                    continue

            # Gather data
            transform = world.get_component(entity_id, TransformComponent)
            action_buffer = world.get_component(entity_id, ActionBufferComponent)
            reward = world.get_component(entity_id, RewardComponent)

            # Construct log entry
            entry = {
                "step_dt": dt,
                "entity_id": str(entity_id),
            }

            if transform:
                entry["state"] = {
                    "x": transform.x,
                    "y": transform.y,
                    "rotation": transform.rotation
                }

            if action_buffer and action_buffer.last_executed_intent:
                entry["action"] = action_buffer.last_executed_intent.model_dump()
            else:
                entry["action"] = None

            if reward:
                entry["reward"] = reward.last_action_reward
                entry["cumulative_reward"] = reward.cumulative_reward

            # Write to file
            try:
                handle = self.file_handles[path]
                handle.write(json.dumps(entry) + "\n")
                handle.flush() # Ensure data is written immediately
            except Exception as e:
                logger.error(f"Failed to write to dataset {path}: {e}")

        # Close handles for paths no longer active
        # Create a list of keys to remove to avoid runtime error during iteration
        paths_to_close = [p for p in self.file_handles if p not in active_paths]
        for path in paths_to_close:
            try:
                self.file_handles[path].close()
            except Exception as e:
                logger.error(f"Error closing file {path}: {e}")
            del self.file_handles[path]

@Registry.register_system(phase=SystemPhase.REWARD, modes=[EngineMode.TEACHER, EngineMode.GYMNASIUM])
class EnvironmentJudgeSystem(System):
    """
    Evaluates game state and assigns rewards.
    """
    async def update(self, world: World, dt: float) -> None:
        entities = world.get_components(RewardComponent)

        for entity_id, reward_comp in entities.items():
            # Placeholder logic: Survival reward
            # Real logic would check collisions, goal completion, etc.
            step_reward = 0.1

            reward_comp.last_action_reward = step_reward
            reward_comp.current_reward = step_reward
            reward_comp.cumulative_reward += step_reward
