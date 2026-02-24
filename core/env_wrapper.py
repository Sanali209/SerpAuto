import gymnasium as gym
from gymnasium import spaces
import numpy as np
import asyncio
from core.engine_v2 import SerpentineEngineV2, EngineMode
from components.core import RewardComponent, ActionBufferComponent, PerceptionComponent

class SerpentineGymEnv(gym.Env):
    """
    OpenAI Gymnasium wrapper for the Serpentine Engine.
    Allows training RL agents using Stable-Baselines3 etc.
    """
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, engine: SerpentineEngineV2, target_entities: list, observation_shape=(10, 10), action_adapter=None):
        super().__init__()
        self.engine = engine
        self.target_entities = target_entities
        self.action_adapter = action_adapter
        
        # Dynamic Action Space (Default to discrete 5 if no adapter)
        if hasattr(action_adapter, "action_space"):
            self.action_space = action_adapter.action_space
        else:
            self.action_space = spaces.Discrete(5)
        
        # Dynamic Observation Space
        # Expecting a grid or image
        self.observation_space = spaces.Box(low=0, high=255, shape=observation_shape, dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # In a real scenario, we would reload the scene here
        # self.engine.scene_manager.reload()
        
        # Run one tick to populate perception
        asyncio.run(self.engine.update_once(0.016))

        return self._get_obs(), {}

    def step(self, action):
        # 1. Map gym action to ECS action buffer
        for i, entity in enumerate(self.target_entities):
            buffer = self.engine.world.get_component(entity, ActionBufferComponent)
            if buffer:
                if self.action_adapter:
                    ecs_action = self.action_adapter.map_action(action)
                    buffer.queue.append(ecs_action)
                else:
                    # Fallback or Raw action injection
                    pass

        # 2. Run one engine tick
        asyncio.run(self.engine.update_once(1.0 / 60.0))

        # 3. Collect rewards and observations
        terminated = False
        truncated = False
        reward_sum = 0.0
        
        for entity in self.target_entities:
            rew_comp = self.engine.world.get_component(entity, RewardComponent)
            if rew_comp:
                reward_sum += rew_comp.current_reward
                terminated = terminated or rew_comp.is_terminated
                truncated = truncated or rew_comp.is_truncated
                # Reset reward for next step
                rew_comp.current_reward = 0.0

        return self._get_obs(), reward_sum, terminated, truncated, {}

    def _get_obs(self):
        # Extract observation from the first target entity's PerceptionComponent
        if not self.target_entities:
            return np.zeros(self.observation_space.shape, dtype=np.float32)

        entity = self.target_entities[0]
        perc = self.engine.world.get_component(entity, PerceptionComponent)

        if perc and "grid" in perc.raw_context:
            return np.array(perc.raw_context["grid"], dtype=np.float32)

        # Fallback
        return np.zeros(self.observation_space.shape, dtype=np.float32)

    def render(self):
        # Optional: trigger ModernGL or DPG rendering
        pass

    def close(self):
        pass
