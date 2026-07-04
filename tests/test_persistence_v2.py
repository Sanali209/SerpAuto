import unittest
import json
import os
import shutil
import tempfile
import gzip
from uuid import uuid4
import sys
from unittest.mock import MagicMock, patch

# Mock dearpygui before importing engine
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()

from serpentine.core.world import World
from serpentine.core.engine import SerpentineEngine, EngineMode
from serpentine.components.standard import TransformComponent
from serpentine.core.entity import EntityID

class TestPersistenceV2(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.engine = SerpentineEngine(mode=EngineMode.PRODUCTION)
        self.engine.world = World() # Reset world

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_world_config(self):
        """Test that World.config is serialized/deserialized."""
        self.engine.world.config["test_key"] = 123
        snapshot = self.engine.world.take_snapshot()
        self.assertEqual(snapshot["config"]["test_key"], 123)

        # Create new world instance to test restoration fully
        new_world = World()
        new_world.restore_snapshot(snapshot)

        # Check if config is updated properly
        self.assertIn("test_key", new_world.config)
        self.assertEqual(new_world.config["test_key"], 123)

    def test_snapshot_compression(self):
        """Test saving and loading compressed snapshots (.json.gz)."""
        # Setup world
        self.engine.world.config["compressed"] = True
        uid = uuid4()
        eid = self.engine.world.create_entity(uid)
        self.engine.world.add_component(eid, TransformComponent(x=10.0, y=20.0))

        # Save compressed
        filepath = os.path.join(self.test_dir, "test.json.gz")
        self.engine.save_snapshot(filepath)

        self.assertTrue(os.path.exists(filepath))

        # Verify it is gzipped
        try:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
                self.assertEqual(data["config"]["compressed"], True)
        except OSError:
            self.fail("File is not a valid gzip file")

        # Clear and load
        self.engine.world = World()
        self.engine.load_snapshot(filepath)

        self.assertEqual(self.engine.world.config["compressed"], True)

        # Check entity restored
        # TransformComponent might need to be imported if not registered?
        # But Registry.register_component handles it on import.
        # Since we imported it at top level, it should be registered.

        comps = self.engine.world.get_components(TransformComponent)
        self.assertEqual(len(comps), 1)
        # Verify value
        # We need to iterate
        comp = next(iter(comps.values()))
        self.assertEqual(comp.x, 10.0)

if __name__ == '__main__':
    unittest.main()
