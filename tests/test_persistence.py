import pytest
import sys
from unittest.mock import MagicMock

# Mock dearpygui before importing anything else that might import it
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()

import json
import os
from uuid import uuid4
from typing import Dict, Any

from serpentine.core.world import World
from serpentine.core.registry import Registry, EngineMode
from serpentine.core.component import BaseComponent
from serpentine.core.engine import SerpentineEngine
from serpentine.core.event_bus import GUIEventBus

# Define a test component
@Registry.register_component
class TestComponent(BaseComponent):
    value: int = 0
    name: str = "test"

# Define another test component
@Registry.register_component
class AnotherComponent(BaseComponent):
    active: bool = True

def test_world_snapshot_restore():
    world = World()

    # Create entity 1 with TestComponent
    e1 = world.create_entity()
    world.add_component(e1, TestComponent(value=10, name="entity1"))

    # Create entity 2 with TestComponent and AnotherComponent
    e2 = world.create_entity()
    world.add_component(e2, TestComponent(value=20, name="entity2"))
    world.add_component(e2, AnotherComponent(active=False))

    # Take snapshot
    snapshot = world.take_snapshot()

    # Verify snapshot structure
    assert "entities" in snapshot
    assert len(snapshot["entities"]) == 2

    # Verify content
    e1_data = next(e for e in snapshot["entities"] if e["uid"] == str(e1))
    assert e1_data["components"]["TestComponent"]["value"] == 10

    e2_data = next(e for e in snapshot["entities"] if e["uid"] == str(e2))
    assert e2_data["components"]["TestComponent"]["value"] == 20
    assert e2_data["components"]["AnotherComponent"]["active"] is False

    # Restore snapshot to a new world
    new_world = World()
    new_world.restore_snapshot(snapshot)

    # Verify entities in new world
    # Note: EntityIDs should be preserved because we serialized UUIDs
    assert new_world.has_component(e1, TestComponent)
    assert new_world.has_component(e2, TestComponent)
    assert new_world.has_component(e2, AnotherComponent)

    # Check values
    c1 = new_world.get_component(e1, TestComponent)
    assert c1.value == 10
    assert c1.name == "entity1"

    c2 = new_world.get_component(e2, TestComponent)
    assert c2.value == 20

    c3 = new_world.get_component(e2, AnotherComponent)
    assert c3.active is False

def test_engine_pause_resume():
    # Use PRODUCTION mode to avoid GUI systems (DPG dependency)
    engine = SerpentineEngine(mode=EngineMode.PRODUCTION)

    assert not engine.paused

    engine.pause()
    assert engine.paused

    engine.play()
    assert not engine.paused

def test_engine_step():
    engine = SerpentineEngine(mode=EngineMode.PRODUCTION)

    engine.pause()
    assert engine.paused

    engine.step()
    assert engine.paused
    assert engine._step_requested

    # Simulate a tick
    # We need to run _tick async
    import asyncio

    async def run_tick():
        await engine._tick(0.1)

    asyncio.run(run_tick())

    # After tick, _step_requested should be False, but paused should remain True
    assert engine.paused
    assert not engine._step_requested

def test_engine_snapshot_file_io(tmp_path):
    engine = SerpentineEngine(mode=EngineMode.PRODUCTION)

    # Setup world state
    e1 = engine.world.create_entity()
    engine.world.add_component(e1, TestComponent(value=99))

    filepath = tmp_path / "test_snapshot.json"
    str_filepath = str(filepath)

    # Test Save
    engine.save_snapshot(str_filepath)
    assert filepath.exists()

    with open(filepath, 'r') as f:
        data = json.load(f)
        assert len(data["entities"]) == 1

    # Clear world
    engine.world = World()
    assert not engine.world.has_component(e1, TestComponent)

    # Test Load
    engine.load_snapshot(str_filepath)

    # Verify
    # Note: e1 is an EntityID (UUID wrapper). The restored world will have the same UUID.
    # We need to reconstruct the EntityID from the string in snapshot or just check existence using the original ID.
    assert engine.world.has_component(e1, TestComponent)
    c = engine.world.get_component(e1, TestComponent)
    assert c.value == 99

def test_gui_event_bus_integration():
    engine = SerpentineEngine(mode=EngineMode.PRODUCTION)

    GUIEventBus.publish("ENGINE_PAUSE")
    assert engine.paused

    GUIEventBus.publish("ENGINE_PLAY")
    assert not engine.paused

    GUIEventBus.publish("ENGINE_STEP")
    assert engine.paused
    assert engine._step_requested

    GUIEventBus.publish("ENGINE_SET_TPS", 120)
    assert engine.target_tps == 120
