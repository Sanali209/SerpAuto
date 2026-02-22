import unittest
import asyncio
import os
import json
from core.engine_v2 import SerpentineEngineV2, EngineMode, Phase
from core.scene import SceneManager
from core.registry import Registry
from core.world import World
from systems.games.snake import SnakeLocomotionSystem
from components.snake import GridPositionComponent

class TestSceneManagement(unittest.TestCase):
    def setUp(self):
        self.filename = "test_scene.json"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_save_and_load_scene(self):
        # 1. Create a "Source" Engine state
        engine = SerpentineEngineV2(mode=EngineMode.GYMNASIUM)
        engine.tick_rate = 123

        # Add a specific system
        loco_sys = SnakeLocomotionSystem()
        engine.add_system(loco_sys, Phase.INTERNAL_PHYSICS)

        # Add an entity
        ent = engine.world.add_entity()
        engine.world.add_component(ent, GridPositionComponent(x=42, y=42))

        # 2. Save Scene
        SceneManager.save_scene(self.filename, engine)

        # Verify file exists
        self.assertTrue(os.path.exists(self.filename))

        # 3. Create a "Target" Engine (Fresh)
        new_engine = SerpentineEngineV2(mode=EngineMode.ARCHITECT) # Different default

        # 4. Load Scene
        SceneManager.load_scene(self.filename, new_engine)

        # 5. Verify State Restoration
        # Check Settings
        self.assertEqual(new_engine.mode, EngineMode.GYMNASIUM)
        self.assertEqual(new_engine.tick_rate, 123)

        # Check Systems
        # We expect SnakeLocomotionSystem to be present
        has_loco = False
        for sys in new_engine.systems_by_phase[Phase.INTERNAL_PHYSICS]:
            if isinstance(sys, SnakeLocomotionSystem):
                has_loco = True
                break
        self.assertTrue(has_loco, "SnakeLocomotionSystem was not restored")

        # Check Entities
        ents = new_engine.world.get_entities_with(GridPositionComponent)
        self.assertEqual(len(ents), 1)
        ent_id = list(ents)[0]
        pos = new_engine.world.get_component(ent_id, GridPositionComponent)
        self.assertEqual(pos.x, 42)

if __name__ == '__main__':
    unittest.main()
