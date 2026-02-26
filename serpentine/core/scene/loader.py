import json
from pathlib import Path
from typing import Dict, Any

from serpentine.core.registry import Registry
from serpentine.core.world import World
from serpentine.core.scene.validator import SceneData

class SceneLoader:
    @staticmethod
    def load_scene(world: World, filepath: str) -> None:
        """
        Loads a scene from a JSON file into the World.
        Clears the existing world state first via world.restore_snapshot.

        Args:
            world: The World instance to populate.
            filepath: Path to the scene JSON file.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Scene file not found: {filepath}")

        with open(path, 'r') as f:
            data = json.load(f)

        # Validate schema
        try:
            scene = SceneData.model_validate(data)
        except Exception as e:
            raise ValueError(f"Invalid scene format in {filepath}: {e}")

        # Prepare snapshot for World.restore_snapshot
        # We convert the list of EntityData objects back to the dictionary format
        # expected by World.restore_snapshot.
        entities_list = []
        for entity in scene.entities:
            if hasattr(entity, 'model_dump'):
                entities_list.append(entity.model_dump())
            else:
                # Fallback: if pydantic is missing, nested models might be dicts
                entities_list.append(entity)

        snapshot = {
            "entities": entities_list
        }

        # Restore entities
        world.restore_snapshot(snapshot)

        # Apply System Configurations (Registry updates)
        # This modifies global Registry state to match scene settings.
        Registry.reset_system_metadata()

        for sys_conf in scene.systems:
            # Handle potential dict if pydantic is missing
            if isinstance(sys_conf, dict):
                name = sys_conf.get("name")
                priority = sys_conf.get("priority_override")
                tick_rate = sys_conf.get("tick_rate_override")
            else:
                name = sys_conf.name
                priority = sys_conf.priority_override
                tick_rate = sys_conf.tick_rate_override

            if name in Registry._system_metadata:
                meta = Registry._system_metadata[name]

                if priority is not None:
                    meta.priority = priority

                if tick_rate is not None:
                    meta.tick_rate = tick_rate

        # Global Config
        # Currently World doesn't have a standardized global config dictionary.
        # Future phases might add World.config or similar.
        # For now, we ignore scene.global_config or log it.
