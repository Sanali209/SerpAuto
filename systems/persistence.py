import json
import os
from typing import Dict, Any
from core.world import World
from core.registry import Registry

class PersistenceSystem:
    """Handles snapshotting the world state and performing time travel."""
    
    @staticmethod
    def snapshot_world(world: World, filepath: str):
        """Dumps the entire world ECS state to a JSON file."""
        data = world.serialize()
        with open(filepath, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"World snapshotted to {filepath}")

    @staticmethod
    def load_snapshot(world: World, filepath: str):
        """Restores the world ECS state from a JSON file."""
        if not os.path.exists(filepath):
            print(f"Snapshot not found: {filepath}")
            return
            
        with open(filepath, 'r', encoding="utf-8") as f:
            data = json.load(f)
            
        component_registry = Registry.get_all_components()
        world.deserialize(data, component_registry)
        print(f"World state restored from {filepath}")

    @staticmethod
    def save_blueprint(config_data: dict, filepath: str):
        """Saves a project's logic blueprint (BT structure, DAG config)."""
        with open(filepath, 'w', encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

    @staticmethod
    def load_blueprint(filepath: str) -> dict:
        """Loads a project's logic blueprint."""
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r', encoding="utf-8") as f:
            return json.load(f)
