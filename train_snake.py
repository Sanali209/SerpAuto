import os
import sys
import argparse
from typing import Optional

try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_checker import check_env
    from stable_baselines3.common.callbacks import CheckpointCallback
except ImportError:
    print("Stable Baselines 3 is not installed. Please install it to train agents.")
    print("pip install stable-baselines3 shimmy>=0.2.1")
    sys.exit(1)

# Add repo root to path if needed
sys.path.append(os.getcwd())

from serpentine.core.gym_wrapper import SerpentineGymEnv

def train_snake(
    total_timesteps: int = 100_000,
    save_path: str = "models/snake_ppo",
    grid_size: int = 10
):
    print(f"Starting training on {grid_size}x{grid_size} grid...")

    # Create environment
    env = SerpentineGymEnv(grid_size=(grid_size, grid_size))

    # Optional: Verify environment
    # check_env(env)

    # Create model
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./logs/snake_tensorboard/")

    # Callbacks
    checkpoint_callback = CheckpointCallback(save_freq=10000, save_path='./models/checkpoints/',
                                             name_prefix='snake_model')

    # Train
    try:
        model.learn(total_timesteps=total_timesteps, callback=checkpoint_callback)
    except KeyboardInterrupt:
        print("Training interrupted.")

    # Save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    print(f"Model saved to {save_path}.zip")

    env.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Snake AI using PPO")
    parser.add_argument("--steps", type=int, default=100_000, help="Total training timesteps")
    parser.add_argument("--grid", type=int, default=10, help="Grid size (NxN)")
    parser.add_argument("--output", type=str, default="models/snake_ppo", help="Output model path")

    args = parser.parse_args()

    train_snake(total_timesteps=args.steps, save_path=args.output, grid_size=args.grid)
