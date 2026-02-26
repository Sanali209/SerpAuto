import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from serpentine.core.registry import Registry
from serpentine.core.world import World
from serpentine.core.scene.validator import SceneData, SceneMetadata, SystemConfig, EntityData

class SceneSaver:
    @staticmethod
    def save_scene(world: World, filepath: str, name: str = "Scene", description: str = "") -> None:
        """
        Serializes the current World state and Registry configuration into a Scene JSON file.

        Args:
            world: The World instance to save.
            filepath: The path to save the JSON file to.
            name: The name of the scene.
            description: A description of the scene.
        """

        # 1. Create Metadata
        metadata = SceneMetadata(
            name=name,
            description=description,
            created_at=datetime.now().isoformat()
        )

        # 2. Serialize Systems
        # Note: Currently we save all registered systems as enabled by default.
        # In the future, we might want to track which systems are actually active in the engine.
        systems = []
        # Accessing protected member _system_metadata - acceptable within core package
        for sys_name, sys_meta in Registry._system_metadata.items():
            config = SystemConfig(
                name=sys_name,
                enabled=True, # Default assumption
                priority_override=sys_meta.priority,
                tick_rate_override=sys_meta.tick_rate,
                config={} # System-specific config not yet standardized
            )
            systems.append(config)

        # Sort systems by name for deterministic output
        systems.sort(key=lambda x: x.name)

        # 3. Serialize Entities
        snapshot = world.take_snapshot()
        entities_raw = snapshot.get("entities", [])

        entities = []
        for ent_dict in entities_raw:
            try:
                entity_data = EntityData(
                    uid=ent_dict["uid"],
                    components=ent_dict["components"]
                )
                entities.append(entity_data)
            except Exception as e:
                # Log error but continue? Or raise?
                # Using print for now as logger might not be configured in this context
                print(f"Error serializing entity {ent_dict.get('uid')}: {e}")

        # 4. Global Config (Placeholder)
        global_config: Dict[str, Any] = {}

        # 5. Create SceneData object
        scene_data = SceneData(
            metadata=metadata,
            systems=systems,
            entities=entities,
            global_config=global_config
        )

        # 6. Write to file
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            # Use json.dumps for compatibility with fallback Pydantic implementation
            # model_dump_json is not available in the fallback
            f.write(json.dumps(scene_data.model_dump(), indent=2))
