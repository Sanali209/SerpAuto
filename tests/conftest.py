import sys
from unittest.mock import MagicMock
import pytest

# Mock dearpygui before any imports
# This is necessary because some modules import dearpygui at the top level
# and we don't want to install it in the test environment if not needed,
# or if it requires a display.

def pytest_configure(config):
    if 'dearpygui.dearpygui' not in sys.modules:
        dpg_mock = MagicMock()

        # Setup common dpg constants/functions that might be accessed
        dpg_mock.mvNode_Attr_Input = 0
        dpg_mock.mvNode_Attr_Output = 1
        dpg_mock.mvNodeCol_TitleBar = 0
        dpg_mock.mvThemeCat_Core = 0
        dpg_mock.mvNode = 0
        dpg_mock.mvNodeCol_TitleBarHovered = 1
        dpg_mock.mvNodeCol_TitleBarSelected = 2

        # Context managers need __enter__ and __exit__
        dpg_mock.window.return_value.__enter__.return_value = None
        dpg_mock.window.return_value.__exit__.return_value = None

        dpg_mock.node_editor.return_value.__enter__.return_value = None
        dpg_mock.node_editor.return_value.__exit__.return_value = None

        dpg_mock.node.return_value.__enter__.return_value = None
        dpg_mock.node.return_value.__exit__.return_value = None

        dpg_mock.node_attribute.return_value.__enter__.return_value = None
        dpg_mock.node_attribute.return_value.__exit__.return_value = None

        dpg_mock.theme.return_value.__enter__.return_value = None
        dpg_mock.theme.return_value.__exit__.return_value = None

        dpg_mock.theme_component.return_value.__enter__.return_value = None
        dpg_mock.theme_component.return_value.__exit__.return_value = None

        dpg_mock.group.return_value.__enter__.return_value = None
        dpg_mock.group.return_value.__exit__.return_value = None

        dpg_mock.child_window.return_value.__enter__.return_value = None
        dpg_mock.child_window.return_value.__exit__.return_value = None

        sys.modules['dearpygui.dearpygui'] = dpg_mock
        sys.modules['dearpygui'] = MagicMock()
        sys.modules['dearpygui'].dearpygui = dpg_mock
