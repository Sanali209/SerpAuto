import unittest
import time
import os
import shutil
from pathlib import Path
from uuid import uuid4
from typing import Any

from serpentine.core.registry import Registry
from serpentine.core.component import BaseComponent
from serpentine.core.world import World
from serpentine.core.scene.manager import SceneManager

# Define test components
class ComponentA(BaseComponent):
    val: int = 0

class ComponentB(BaseComponent):
    name: str = "test"

import copy

class TestSceneLoading(unittest.TestCase):
    def setUp(self):
        # Backup Registry state to prevent side effects
        self._registry_backup = {
            'components': Registry._components.copy(),
            'component_masks': Registry._component_masks.copy(),
            'next_bit_index': Registry._next_bit_index,
            'systems': Registry._systems.copy(),
            # Deep copy metadata because SceneLoader modifies the objects in place
            'system_metadata': copy.deepcopy(Registry._system_metadata),
            'initial_system_metadata': copy.deepcopy(Registry._initial_system_metadata)
        }

        self.world = World()
        self.manager = SceneManager(self.world)
        self.test_dir = Path("tests/temp_scenes")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # Register components if not already registered
        # Note: In a real app, these would be imported from modules where they are decorated.
        Registry.register_component(ComponentA)
        Registry.register_component(ComponentB)

    def tearDown(self):
        # Restore Registry state
        Registry._components = self._registry_backup['components']
        Registry._component_masks = self._registry_backup['component_masks']
        Registry._next_bit_index = self._registry_backup['next_bit_index']
        Registry._systems = self._registry_backup['systems']
        Registry._system_metadata = self._registry_backup['system_metadata']
        Registry._initial_system_metadata = self._registry_backup['initial_system_metadata']

        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_registry_bitmasks(self):
        mask_a = Registry.get_component_mask(ComponentA)
        mask_b = Registry.get_component_mask(ComponentB)

        self.assertGreater(mask_a, 0)
        self.assertGreater(mask_b, 0)
        self.assertNotEqual(mask_a, mask_b)
        self.assertTrue((mask_a & (mask_a - 1)) == 0, "Bitmask A is not power of 2")
        self.assertTrue((mask_b & (mask_b - 1)) == 0, "Bitmask B is not power of 2")

    def test_save_and_load_scene(self):
        # Create entities
        e1 = self.world.create_entity()
        self.world.add_component(e1, ComponentA(val=10))

        e2 = self.world.create_entity()
        self.world.add_component(e2, ComponentB(name="entity2"))

        filepath = self.test_dir / "test_scene.json"

        # Save
        self.manager.save_scene(str(filepath), name="Test Scene")
        self.assertTrue(filepath.exists())

        # Clear world manually to ensure load works
        self.world = World()
        self.manager = SceneManager(self.world)

        # Load
        self.manager.load_scene(str(filepath))

        # Verify
        self.assertEqual(len(self.world._entities), 2)

        # Check components
        comps_a = self.world.get_components(ComponentA)
        self.assertEqual(len(comps_a), 1)
        self.assertEqual(list(comps_a.values())[0].val, 10)

        comps_b = self.world.get_components(ComponentB)
        self.assertEqual(len(comps_b), 1)
        self.assertEqual(list(comps_b.values())[0].name, "entity2")

    def test_performance_1000_entities(self):
        # Create 1000 entities with ComponentA
        for i in range(1000):
            e = self.world.create_entity()
            self.world.add_component(e, ComponentA(val=i))

        filepath = self.test_dir / "perf_scene.json"

        # Save first
        self.manager.save_scene(str(filepath))

        # Reset world
        self.world = World()
        self.manager = SceneManager(self.world)

        # Measure Load Time
        start_time = time.time()
        self.manager.load_scene(str(filepath))
        end_time = time.time()

        duration = (end_time - start_time) * 1000 # ms
        print(f"Load time for 1000 entities: {duration:.2f}ms")

        self.assertLess(duration, 500, "Scene loading took longer than 500ms")
        self.assertEqual(len(self.world._entities), 1000)

if __name__ == '__main__':
    unittest.main()
