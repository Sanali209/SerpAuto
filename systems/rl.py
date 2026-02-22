from core.system import System
from core.world import World
from components.internal import RewardComponent

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
