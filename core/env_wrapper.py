import gymnasium as gym
from gymnasium import spaces
import numpy as np
import asyncio
from core.engine_v2 import SerpentineEngineV2, EngineMode
from components.core import RewardComponent, ActionBufferComponent

class SerpentineGymEnv(gym.Env):
    """
    OpenAI Gymnasium wrapper for the Serpentine Engine.
    Allows training RL agents using Stable-Baselines3 etc.
    """
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, engine: SerpentineEngineV2, target_entities: list):
        super().__init__()
        self.engine = engine
        self.target_entities = target_entities
        
        # Define action and observation spaces
        # Placeholder: assume 4 discrete actions (Stay, Up, Down, Left, Right)
        self.action_space = spaces.Discrete(5)
        
        # Observation space: Placeholder (could be image or flat vector)
        self.observation_space = spaces.Box(low=0, high=255, shape=(64, 64, 3), dtype=np.uint8)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Reset world state (needs SceneManager integration for real use)
        # self.engine.world.clear() 
        
        observation = np.zeros((64, 64, 3), dtype=np.uint8)
        info = {}
        return observation, info

    def step(self, action):
        # 1. Map gym action to ECS action buffer
        for i, entity in enumerate(self.target_entities):
            # In mass-vectorized mode, 'action' would be a list
            buffer = self.engine.world.get_component(entity, ActionBufferComponent)
            if buffer:
                # Mock action mapping
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

        observation = np.zeros((64, 64, 3), dtype=np.uint8)
        return observation, reward_sum, terminated, truncated, {}

    def render(self):
        # Optional: trigger ModernGL or DPG rendering
        pass

    def close(self):
        pass
