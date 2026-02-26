import time
import random
import os
import sys

try:
    import numpy as np
except ImportError:
    print("Numpy not installed. Cannot run demo.")
    sys.exit(1)

from serpentine.core.gym_wrapper import SerpentineGymEnv
# Import components to access specific attributes if needed, though obs is enough
from serpentine.components.snake import SnakeBodyComponent

def main():
    try:
        env = SerpentineGymEnv(grid_size=(10, 10))
    except ImportError:
        print("Gymnasium not installed. Cannot run demo.")
        return

    obs, info = env.reset()
    done = False
    truncated = False

    print("Snake Demo Started!")
    print("Use Ctrl+C to stop.")

    steps = 0
    try:
        while not (done or truncated):
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"Step: {steps}")

            # Get snake length for display
            snake = env.engine.world.get_component(env.snake_id, SnakeBodyComponent)
            length = len(snake.segments) if snake else "?"
            print(f"Snake Length: {length}")

            # Simple ASCII rendering
            grid = obs
            render_str = ""
            for row in grid:
                for cell in row:
                    if cell == 0: char = "."
                    elif cell == 1: char = "H"
                    elif cell == 2: char = "o"
                    elif cell == 3: char = "*"
                    else: char = "?"
                    render_str += char + " "
                render_str += "\n"
            print(render_str)

            # Random Action (0=UP, 1=DOWN, 2=LEFT, 3=RIGHT)
            # To make it slightly smarter, try to move towards food?
            # Or just random. Random is fine for demo.
            action = env.action_space.sample()

            obs, reward, done, truncated, info = env.step(action)
            steps += 1
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        env.close()
        print("Demo Finished.")

if __name__ == "__main__":
    main()
