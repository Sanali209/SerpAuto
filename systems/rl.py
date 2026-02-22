from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.internal import RewardComponent

@register_system(phase=Phase.INTERNAL_PHYSICS)
class EnvironmentJudgeSystem(System):
    """
    Evaluates agent actions and assigns rewards.
    Active in GYMNASIUM mode.
    """
    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(RewardComponent)
        for entity in entities:
            reward_comp = world.get_component(entity, RewardComponent)

            # Simple placeholder logic: Reward for existing?
            step_reward = 0.1
            reward_comp.current_reward = step_reward
            reward_comp.cumulative_reward += step_reward
