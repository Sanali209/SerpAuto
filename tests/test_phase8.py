import unittest
import sys
import os
import tempfile
import shutil
import json
from unittest.mock import MagicMock, patch

# Mock libraries not strictly required for logic tests
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()
sys.modules["fastapi"] = MagicMock()

from serpentine.core.engine import SerpentineEngine, EngineMode
from serpentine.modes.config_loader import ModeConfigLoader
from serpentine.systems.base import System
from serpentine.systems.bridge import BridgeSystem

class TestPhase8(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_mode_config_loader(self):
        # Create a dummy config
        config = {
            "excluded_systems": ["SystemA"],
            "tick_rates": {"SystemB": 10}
        }
        path = os.path.join(self.test_dir, "config.json")
        with open(path, 'w') as f:
            json.dump(config, f)

        # Load it
        loaded = ModeConfigLoader.load_config(path)
        self.assertEqual(loaded["excluded_systems"], ["SystemA"])
        self.assertEqual(loaded["tick_rates"]["SystemB"], 10)

    def test_engine_config_integration(self):
        # Create config
        config = {
            "excluded_systems": ["SensoryInputSystem"], # Existing system
            "tick_rates": {}
        }
        path = os.path.join(self.test_dir, "mode_config.json")
        with open(path, 'w') as f:
            json.dump(config, f)

        # Init engine
        engine = SerpentineEngine(mode=EngineMode.PRODUCTION, config_path=path)

        # Check system exclusion
        input_systems = engine.systems.get(engine.systems.keys().__iter__().__next__(), []) # Just check if we can find it
        # Actually check phase INPUT
        from serpentine.core.registry import SystemPhase
        input_systems = engine.systems.get(SystemPhase.INPUT, [])

        system_names = [s.__class__.__name__ for s in input_systems]
        self.assertNotIn("SensoryInputSystem", system_names)

    def test_system_reset(self):
        system = BridgeSystem()
        system._accumulator = 100.0

        # Mock world
        world = MagicMock()

        system.reset(world)
        self.assertEqual(system._accumulator, 0.0)

if __name__ == '__main__':
    unittest.main()
