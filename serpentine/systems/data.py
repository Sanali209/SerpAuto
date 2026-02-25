import json
import logging
from typing import Optional, Dict, Any
from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.components.simulation import DatasetConfigComponent, RewardComponent
from serpentine.perception.components import ActionBufferComponent
from serpentine.components.standard import TransformComponent

logger = logging.getLogger(__name__)

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
