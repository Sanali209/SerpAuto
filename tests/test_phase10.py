import unittest
import sys
import asyncio
from unittest.mock import MagicMock, patch

# Mock libs
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()
sys.modules["stable_baselines3"] = MagicMock()
sys.modules["stable_baselines3.common.env_checker"] = MagicMock()
sys.modules["stable_baselines3.common.callbacks"] = MagicMock()

from serpentine.core.engine import SerpentineEngine, EngineMode
from serpentine.core.event_bus import GUIEventBus
from serpentine.systems.base import System
from serpentine.core.registry import Registry, SystemPhase

@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.ARCHITECT])
class ToggleableTestSystem(System):
    async def update(self, world, dt):
        pass

class TestPhase10(unittest.TestCase):
    def setUp(self):
        self.engine = SerpentineEngine(mode=EngineMode.ARCHITECT)
        # Ensure event bus is clean or mocked?
        # GUIEventBus is singleton, might need reset or just use pub/sub

    def test_dynamic_toggling(self):
        # System should be active initially
        system_name = "ToggleableTestSystem"

        # Check initial state (not excluded)
        self.assertNotIn(system_name, self.engine.mode_config.get("excluded_systems", []))

        # Disable via EventBus
        GUIEventBus.publish("ENGINE_TOGGLE_SYSTEM", {"name": system_name, "enabled": False})

        # Check if added to excluded list
        self.assertIn(system_name, self.engine.mode_config["excluded_systems"])

        # Enable again
        GUIEventBus.publish("ENGINE_TOGGLE_SYSTEM", {"name": system_name, "enabled": True})
        self.assertNotIn(system_name, self.engine.mode_config["excluded_systems"])

    def test_training_script_structure(self):
        # Just import to check syntax/imports
        import train_snake
        self.assertTrue(hasattr(train_snake, 'train_snake'))

if __name__ == '__main__':
    unittest.main()
