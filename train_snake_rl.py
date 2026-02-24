import gymnasium as gym
import numpy as np
import asyncio
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

from core.engine_v2 import SerpentineEngineV2, EngineMode, Phase
from core.env_wrapper import SerpentineGymEnv
from components.core import PerceptionComponent, ActionBufferComponent, RewardComponent, BrainComponent
from components.snake import GridPositionComponent, SnakeBodyComponent, SnakeColliderComponent
from components.internal import VelocityComponent
from systems.games.snake import SnakeLocomotionSystem, SnakeCollisionSystem
from systems.perception import SensoryInputSystem
from perception.pipeline import PerceptionPipelineSystem
from perception.internal_nodes import InternalGridStateNode
from systems.learning import EnvironmentJudgeSystem, ReplayBufferSystem

def setup_snake_world(engine: SerpentineEngineV2):
    world = engine.world
    
    # 1. Create Snake
    snake = world.add_entity()
    world.add_component(snake, GridPositionComponent(x=5, y=5))
    world.add_component(snake, SnakeBodyComponent(length=3, body_segments=[]))
    world.add_component(snake, VelocityComponent(vx=1, vy=0))
    world.add_component(snake, ActionBufferComponent())
    world.add_component(snake, PerceptionComponent())
    world.add_component(snake, RewardComponent())
    world.add_component(snake, BrainComponent())
    
    # 2. Create Apple
    apple = world.add_entity()
    world.add_component(apple, GridPositionComponent(x=2, y=2))
    world.add_component(apple, SnakeColliderComponent(type="apple"))
    
    # 3. Add Systems
    # Note: SensoryInput is skipped for Internal Perception
    engine.add_system(SnakeLocomotionSystem(), Phase.INTERNAL_PHYSICS)
    engine.add_system(SnakeCollisionSystem(), Phase.INTERNAL_PHYSICS)
    
    # RL Logic
    # We use InternalGridStateNode to get O(1) observations
    pipeline = PerceptionPipelineSystem(nodes=[InternalGridStateNode()])
    engine.add_system(pipeline, Phase.PERCEPTION)
    
    # Replay Buffering (Optional for SB3, but good for verification)
    engine.add_system(ReplayBufferSystem(output_path="snake_rl_log.jsonl"), Phase.TELEMETRY)
    
    return [snake]

class SnakeRLWrapper(SerpentineGymEnv):
    """Specific overrides for Snake observation space."""
    def __init__(self, engine, target_entities):
        super().__init__(engine, target_entities)
        # 10x10 grid = 100 features
        self.observation_space = gym.spaces.Box(low=0, high=3, shape=(100,), dtype=np.float32)

    def _get_obs(self):
        entity = self.target_entities[0]
        perception = self.engine.world.get_component(entity, PerceptionComponent)
        obs = perception.raw_context.get("grid_observation", [0]*100)
        return np.array(obs, dtype=np.float32)

    def reset(self, seed=None, options=None):
        # We don't clear the whole world to keep systems
        # Just reset the snake
        entity = self.target_entities[0]
        pos = self.engine.world.get_component(entity, GridPositionComponent)
        body = self.engine.world.get_component(entity, SnakeBodyComponent)
        vel = self.engine.world.get_component(entity, VelocityComponent)
        
        pos.x, pos.y = 5, 5
        body.length = 3
        body.body_segments = []
        vel.vx, vel.vy = 1, 0
        
        return self._get_obs(), {}

    def step(self, action):
        # Action Map: 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT, 4: STAY
        entity = self.target_entities[0]
        vel = self.engine.world.get_component(entity, VelocityComponent)
        
        if action == 0: vel.vx, vel.vy = 0, -1
        elif action == 1: vel.vx, vel.vy = 0, 1
        elif action == 2: vel.vx, vel.vy = -1, 0
        elif action == 3: vel.vx, vel.vy = 1, 0
        
        # Advance engine
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.engine.update_once(0.1))
        
        obs = self._get_obs()
        rew_comp = self.engine.world.get_component(entity, RewardComponent)
        reward = rew_comp.current_reward
        terminated = rew_comp.is_terminated
        truncated = rew_comp.is_truncated
        
        # Reset reward for next step
        rew_comp.current_reward = 0.0
        
        return obs, reward, terminated, truncated, {}

def main():
    print("Initializing Serpentine RL Training for Snake...")
    engine = SerpentineEngineV2(mode=EngineMode.GYMNASIUM)
    agents = setup_snake_world(engine)
    
    env = SnakeRLWrapper(engine, agents)
    
    print("Verifying Environment...")
    # check_env(env)
    
    print("Starting PPO Training...")
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=1000)
    
    print("Training Complete. Saving model...")
    model.save("snake_ppo_model")

if __name__ == "__main__":
    main()
