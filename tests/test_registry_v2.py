import pytest
from serpentine.core.registry_v2 import RegistryV2, RegistryMeta
from serpentine.core.selection import SelectionService
from serpentine.core.event_bus import GUIEventBus

def test_registry_v2_registration():
    @RegistryV2.register_node(category="TestCat", icon="T", description="Test Node")
    class TestNode:
        pass

    @RegistryV2.register_window(category="TestWin", icon="W", description="Test Window")
    class TestWindow:
        pass

    # Check node metadata
    meta = RegistryV2.get_node_metadata("TestNode")
    assert meta is not None
    assert meta.category == "TestCat"
    assert meta.icon == "T"
    assert meta.description == "Test Node"

    # Check window metadata
    meta = RegistryV2.get_window_metadata("TestWindow")
    assert meta is not None
    assert meta.category == "TestWin"

    # Check filtering
    nodes = RegistryV2.get_nodes_by_category("TestCat")
    assert TestNode in nodes

    windows = RegistryV2.get_windows_by_category("TestWin")
    assert TestWindow in windows

def test_selection_service():
    received_event = None

    def on_change(data):
        nonlocal received_event
        received_event = data

    GUIEventBus.subscribe("ON_SELECTION_CHANGED", on_change)

    item = "Entity123"
    item_type = "ENTITY"

    SelectionService.set_selected(item, item_type)

    assert SelectionService.get_selected() == item
    assert SelectionService.get_selected_type() == item_type
    assert received_event is not None
    assert received_event["item"] == item
    assert received_event["type"] == item_type

    SelectionService.clear_selection()
    assert SelectionService.get_selected() is None
