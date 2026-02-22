import argparse
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine_v2 import SerpentineEngineV2, EngineMode
from core.scene import SceneManager
from core.registry import Registry

# Import all modules to trigger registration
# In a real app this might be dynamic or in __init__.py
import components.core
import components.spatial
import components.web
import components.domain
import components.internal
import components.snake

import systems.action
import systems.perception
import systems.brain
import systems.swarm
import systems.telemetry
import systems.input
import systems.rl
import systems.advanced
import systems.games.snake

def main():
    parser = argparse.ArgumentParser(description="Serpentine Engine Headless Loader")
    parser.add_argument("--scene", type=str, help="Path to scene JSON file", required=False)
    parser.add_argument("--mode", type=str, default="ARCHITECT",
                        choices=["ARCHITECT", "PRODUCTION", "TEACHER", "GYMNASIUM"],
                        help="Operation Mode override")
    parser.add_argument("--tick-rate", type=int, help="Override tick rate", required=False)

    args = parser.parse_args()

    print(f"Initializing Serpentine Engine...")

    # 1. Determine Mode
    try:
        mode = EngineMode[args.mode]
    except KeyError:
        mode = EngineMode.ARCHITECT

    engine = SerpentineEngineV2(mode=mode)

    # 2. Load Scene if provided
    if args.scene:
        print(f"Loading scene from {args.scene}...")
        try:
            SceneManager.load_scene(args.scene, engine)
            print("Scene loaded successfully.")
        except Exception as e:
            print(f"Error loading scene: {e}")
            return
    else:
        print("No scene provided. Starting empty engine.")

    # 3. Apply Overrides
    if args.tick_rate:
        engine.tick_rate = args.tick_rate

    print(f"Starting Engine in {mode.name} mode at {engine.tick_rate} TPS...")

    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        print("\nEngine stopped by user.")

if __name__ == "__main__":
    main()
