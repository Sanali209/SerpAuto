import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock dearpygui before importing GUI system
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()
import dearpygui.dearpygui as dpg

# Now import system
from serpentine.systems.gui.system import GUIDebugSystem
from serpentine.systems.gui.selection import SelectionService
from serpentine.systems.gui.base import GUIEventBus
from serpentine.core.world import World
from serpentine.core.entity import EntityID

class TestGUILogic(unittest.TestCase):
    def setUp(self):
        # Create fresh world for each test
        self.world = World()
        # Create some entities
        self.e1 = self.world.create_entity()
        self.e2 = self.world.create_entity()

        # Create system, mocking dpg calls
        self.system = GUIDebugSystem()
        self.system.window_manager.update = MagicMock()

        # Reset selection
        SelectionService.clear_selection()

        # Mock DPG context creation
        dpg.create_context = MagicMock()
        dpg.create_viewport = MagicMock()
        dpg.setup_dearpygui = MagicMock()
        dpg.configure_app = MagicMock()
        dpg.show_viewport = MagicMock()

        # Initialize DPG context mock
        self.system.setup_dpg()

    def test_selection_service(self):
        """Verify SelectionService updates global state and notifies listeners."""
        listener = MagicMock()
        GUIEventBus.subscribe("SELECTION_CHANGED", listener)

        SelectionService.set_selected(self.e1, "ENTITY")

        self.assertEqual(SelectionService.get_selected(), self.e1)
        self.assertEqual(SelectionService.get_selected_type(), "ENTITY")

        # Check if listener was called
        listener.assert_called()
        call_args = listener.call_args[0][0] # First arg of last call
        self.assertEqual(call_args["item"], self.e1)
        self.assertEqual(call_args["type"], "ENTITY")

    def test_window_registration(self):
        """Verify windows are registered in the manager."""
        manager = self.system.window_manager

        # Check window types/tags
        tags = manager.windows.keys()
        self.assertIn("control_deck", tags)
        self.assertIn("outliner", tags)
        self.assertIn("inspector", tags)
        # Fix: viewport window tag is "viewport_window"
        self.assertIn("viewport_window", tags)
        # New windows
        self.assertIn("bt_editor", tags)
        self.assertIn("perception_editor", tags)

    def test_outliner_logic(self):
        """Verify Outliner populates entity list (logic check)."""
        outliner = self.system.window_manager.get_window("outliner")
        self.assertIsNotNone(outliner)

        # Mock DPG functions used in update
        dpg.get_item_children.return_value = []
        dpg.delete_item.return_value = None
        dpg.add_selectable.return_value = None

        # Reset mock calls
        dpg.add_selectable.reset_mock()

        outliner.update(self.world, 0.1)

        # Should add selectable for e1 and e2
        self.assertEqual(dpg.add_selectable.call_count, 2)

        # Inspect calls
        calls = dpg.add_selectable.call_args_list
        # user_data is in kwargs
        user_datas = [c.kwargs.get('user_data') for c in calls]

        # Check if e1 and e2 are in user_datas
        self.assertIn(self.e1, user_datas)
        self.assertIn(self.e2, user_datas)

if __name__ == "__main__":
    # Clear event bus subscribers before running
    GUIEventBus._subscribers = {}
    unittest.main()
