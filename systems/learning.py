import json
import os
import logging
from typing import List, Dict, Any
from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import BrainComponent, RewardComponent

logger = logging.getLogger(__name__)

@register_system(phase=Phase.REWARD)
class EnvironmentJudgeSystem(System):
    """
    Evaluates game rules and updates RewardComponent.
    """
    async def update(self, world: World, dt: float):
        # Placeholder: In a real game, this would check for collisions with food/enemies
        # and set world.get_component(entity, RewardComponent).current_reward
        pass

@register_system(phase=Phase.TELEMETRY)
class ReplayBufferSystem(System):
    """
    Collects MDP transitions (s, a, r, s') and flushes them to a buffer or file.
    Only processes entities in READY_TO_LEARN state.
    """
    def __init__(self, output_path: str = "experience_replay.jsonl"):
        self.output_path = output_path
        self.buffer: List[Dict[str, Any]] = []

    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(BrainComponent, RewardComponent)
        
        for entity in entities:
            brain = world.get_component(entity, BrainComponent)
            reward = world.get_component(entity, RewardComponent)
            
            if brain.status == "READY_TO_LEARN":
                # Create transition record
                transition = {
                    "entity_id": str(entity),
                    "state": brain.last_state,
                    "action": brain.last_action,
                    "reward": reward.current_reward,
                    "terminated": reward.is_terminated,
                    "truncated": reward.is_truncated,
                    "timestamp": world.engine_time if hasattr(world, "engine_time") else 0
                }
                
                self.buffer.append(transition)
                
                # Reset for next loop
                brain.status = "IDLE"
                reward.current_reward = 0.0
                
                # Periodic flush
                if len(self.buffer) >= 100:
                    self.flush()

    def flush(self):
        if not self.buffer:
            return
            
        try:
            with open(self.output_path, "a") as f:
                for entry in self.buffer:
                    f.write(json.dumps(entry) + "\n")
            self.buffer.clear()
            logger.info(f"Flushed {len(self.buffer)} transitions to {self.output_path}")
        except Exception as e:
            logger.error(f"Failed to flush replay buffer: {e}")
