import asyncio
import sys
import os

# Add repo root to path if needed (e.g. running from root)
sys.path.append(os.getcwd())

try:
    from serpentine.core.engine import SerpentineEngine, EngineMode
    from serpentine.core.world import World
    from serpentine.components.snake import SnakeBodyComponent, SnakeFoodComponent, SnakeConfigComponent
    from serpentine.components.standard import StatsComponent, TransformComponent
    from serpentine.components.simulation import RewardComponent, InputControlComponent
    from serpentine.perception.components import ActionBufferComponent, PerceptionComponent
except ImportError as e:
    print(f"Error importing Serpentine modules: {e}")
    sys.exit(1)

async def main():
    print("Starting Snake Game...")

    # Initialize Engine in ARCHITECT mode to enable GUI and Input systems
    engine = SerpentineEngine(mode=EngineMode.ARCHITECT, target_tps=60)

    world = engine.world

    # Create Snake Entity
    snake_id = world.create_entity()
    # Initial segments: (10,10) is head, followed by body
    segments = [(10, 10), (10, 11), (10, 12)]

    world.add_component(snake_id, SnakeBodyComponent(
        segments=segments,
        current_direction="UP",
        next_direction="UP"
    ))

    # Config: Grid 20x20, Move every 0.15s
    world.add_component(snake_id, SnakeConfigComponent(
        grid_width=20,
        grid_height=20,
        move_interval=0.15
    ))

    # Enable Input Control
    world.add_component(snake_id, InputControlComponent(enabled=True))

    # Action Buffer to store KeyIntents/ChangeDirectionIntents
    world.add_component(snake_id, ActionBufferComponent())

    # Stats and Reward for game logic
    world.add_component(snake_id, StatsComponent(is_alive=True))
    world.add_component(snake_id, RewardComponent())

    # Perception Component (required by SnakeStateReaderSystem)
    world.add_component(snake_id, PerceptionComponent())

    # Create Food Entity
    food_id = world.create_entity()
    world.add_component(food_id, SnakeFoodComponent(value=1))
    # TransformComponent stores Food position
    world.add_component(food_id, TransformComponent(x=5.0, y=5.0, z=0.0))

    print("Game Initialized.")
    print("Controls: W/A/S/D or Arrow Keys.")

    try:
        await engine.run()
    except KeyboardInterrupt:
        print("Game Stopped.")

if __name__ == "__main__":
    asyncio.run(main())
