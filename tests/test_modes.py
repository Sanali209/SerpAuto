import unittest
import sys
from unittest.mock import MagicMock

# Mock dearpygui before imports
sys.modules['dearpygui'] = MagicMock()
sys.modules['dearpygui.dearpygui'] = MagicMock()
sys.modules['typer'] = MagicMock() # Just in case

import os
# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from serpentine.core.engine import SerpentineEngine
from serpentine.core.registry import EngineMode
from serpentine.modes import ArchitectMode, ProductionMode

class TestModesIntegration(unittest.TestCase):
    def test_architect_mode(self):
        engine = SerpentineEngine(mode=EngineMode.ARCHITECT)
        self.assertIsInstance(engine._mode_strategy, ArchitectMode)
        self.assertIsNotNone(engine.systems)

    def test_production_mode(self):
        engine = SerpentineEngine(mode=EngineMode.PRODUCTION)
        self.assertIsInstance(engine._mode_strategy, ProductionMode)

        # Check that no GUI systems are present
        # Iterate over all phases and systems
        for phase, systems in engine.systems.items():
            for system in systems:
                # system is an instance, so we check type
                module_name = system.__class__.__module__
                self.assertNotIn('serpentine.systems.gui', module_name,
                                 f"GUI system {system.__class__.__name__} found in Production mode!")

if __name__ == '__main__':
    unittest.main()
