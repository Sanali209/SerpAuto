import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from core.engine_v2 import SerpentineEngineV2, EngineMode, Phase
from core.registry import Registry
from core.world import World

class SceneSettings(BaseModel):
    tick_rate: int = 60
    mode: str = "ARCHITECT" # String representation of EngineMode

class SceneData(BaseModel):
    systems: List[str] = [] # List of System Class Names
    entities: Dict[str, Any] = {} # Serialized entities (World dump format)
    settings: SceneSettings = SceneSettings()

class SceneManager:
    @staticmethod
    def save_scene(filepath: str, engine: SerpentineEngineV2):
        """Saves current engine state (Systems + World + Settings) to a scene file."""

        # 1. Get Active Systems
        # We need a flat list of system names.
        # engine.systems_by_phase contains them.
        system_names = []
        for phase in Phase:
            for system in engine.systems_by_phase[phase]:
                system_names.append(type(system).__name__)

        # 2. Serialize World
        # World.serialize returns a JSON string, we need dict for embedding in SceneData
        world_json_str = engine.world.serialize()
        world_data = json.loads(world_json_str) # TODO: Optimize World.serialize to return dict

        # 3. Settings
        settings = SceneSettings(
            tick_rate=engine.tick_rate,
            mode=engine.mode.name
        )

        # 4. Construct SceneData
        # world_data has "entities" and "components" keys.
        # Our SceneData.entities expect that structure.
        # But wait, SceneData.entities is defined as Dict[str, Any] which maps to the root of world dump.

        scene = SceneData(
            systems=system_names,
            entities=world_data,
            settings=settings
        )

        with open(filepath, 'w') as f:
            f.write(scene.model_dump_json(indent=2))

    @staticmethod
    def load_scene(filepath: str, engine: SerpentineEngineV2):
        """Loads a scene file, configuring the engine and populating the world."""

        with open(filepath, 'r') as f:
            json_data = f.read()

        scene = SceneData.model_validate_json(json_data)

        # 1. Configure Settings
        try:
            mode = EngineMode[scene.settings.mode]
            engine.mode = mode
        except KeyError:
            print(f"Warning: Unknown mode {scene.settings.mode}, defaulting to ARCHITECT")
            engine.mode = EngineMode.ARCHITECT

        engine.tick_rate = scene.settings.tick_rate

        # 2. Reset Engine Systems
        # We need a way to clear systems.
        # accessing internal dicts directly for now.
        engine.systems_by_phase = {phase: [] for phase in Phase}
        engine.systems = []

        # 3. Instantiate and Add Systems
        for sys_name in scene.systems:
            sys_cls = Registry.get_system(sys_name)
            if sys_cls:
                phase = Registry.get_system_phase(sys_name)
                # Instantiate default
                try:
                    system_instance = sys_cls()
                    engine.add_system(system_instance, phase)
                except Exception as e:
                    print(f"Failed to instantiate system {sys_name}: {e}")
            else:
                print(f"Warning: System {sys_name} not found in Registry.")

        # 4. Deserialize World
        # We assume scene.entities is the dict structure World.deserialize expects
        # But World.deserialize takes a JSON string currently.
        # Let's fix World.deserialize or re-dump. Re-dumping is easier for now to reuse existing code.
        world_dump_str = json.dumps(scene.entities)
        engine.world.deserialize(world_dump_str, Registry.get_all_components())
