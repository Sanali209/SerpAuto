import sys
from unittest.mock import MagicMock, patch
import asyncio

# Setup mocks for dependencies that might be missing in environment
# This must happen before any imports of modules under test

# Mock numpy
try:
    import numpy as np
except ImportError:
    class MockNdArray:
        def __init__(self, shape=(100, 100, 3)):
            self.shape = shape
            self.dtype = "uint8"

        def __getitem__(self, item):
            # Return another mock with default shape for slicing
            return MockNdArray(shape=(20, 20, 3))

    np = MagicMock()
    np.uint8 = "uint8"
    np.ndarray = MockNdArray

    def mock_zeros(shape, *args, **kwargs):
        return MockNdArray(shape)

    def mock_array(obj, *args, **kwargs):
        if hasattr(obj, 'shape'):
            return MockNdArray(obj.shape)
        return MockNdArray()

    np.zeros.side_effect = mock_zeros
    np.array.side_effect = mock_array

    sys.modules["numpy"] = np

# Mock cv2
try:
    import cv2
except ImportError:
    cv2 = MagicMock()
    cv2.COLOR_BGR2GRAY = 6
    cv2.cvtColor = MagicMock()
    cv2.cvtColor.side_effect = lambda img, code: np.zeros((img.shape[0], img.shape[1]))
    cv2.TM_CCOEFF_NORMED = 1
    cv2.matchTemplate.return_value = np.zeros((10, 10))
    sys.modules["cv2"] = cv2

# Mock mss
try:
    import mss
except ImportError:
    mss = MagicMock()
    sys.modules["mss"] = mss

# Mock pyautogui
try:
    import pyautogui
except ImportError:
    pyautogui = MagicMock()
    sys.modules["pyautogui"] = pyautogui

import pytest
from datetime import datetime

# Now import modules under test
from serpentine.perception.types import Observation
from serpentine.perception.nodes import CropNode, GrayscaleNode, DOMParserNode, GridMapperNode
from serpentine.perception.components import PerceptionComponent, ActionBufferComponent
from serpentine.mind.intent import Intent as BaseAction, ClickIntent as ClickAction, MoveIntent as MoveAction, KeyIntent as KeyAction
from serpentine.perception.actions import ActionExecutionSystem
from serpentine.perception.pipeline import PerceptionPipelineSystem
from serpentine.perception.ingestion import SensoryInputSystem
from serpentine.core.world import World

class TestPerceptionNodes:
    def test_crop_node(self):
        node = CropNode("crop")
        img = np.zeros((100, 100, 3))
        obs = Observation(source_node="test", data_type="image", content=img)

        # When using mock numpy, slicing returns (20, 20, 3) per our MockNdArray logic
        res = node.process(obs, roi=(10, 10, 20, 20))
        assert res is not None
        assert res.content.shape == (20, 20, 3)

    def test_grayscale_node(self):
        node = GrayscaleNode("gray")
        img = np.zeros((10, 10, 3))
        obs = Observation(source_node="test", data_type="image", content=img)

        res = node.process(obs)
        assert res is not None
        assert res.data_type == "image"
        # Mock cvtColor -> (10, 10)
        assert res.content.shape == (10, 10)

    def test_dom_parser_stub(self):
        node = DOMParserNode("dom")
        obs = Observation(source_node="test", data_type="dom", content="<html></html>")
        res = node.process(obs)
        assert res is not None
        assert res.data_type == "dom_tree"
        assert isinstance(res.content, dict)

    def test_grid_mapper_node(self):
        node = GridMapperNode("grid")
        obs = Observation(source_node="test", data_type="internal_state", content={})
        res = node.process(obs, grid_size=(5, 5))
        if res:
            assert res.content.shape == (5, 5)

def test_pipeline_execution():
    async def _test():
        world = World()
        entity = world.create_entity()
        comp = PerceptionComponent()
        world.add_component(entity, comp)

        # Add raw observation
        img = np.zeros((1080, 1920, 3))
        obs = Observation(source_node="raw", data_type="image", content=img, metadata={"width": 1920, "height": 1080})
        comp.add_observation("raw_screen", obs)

        system = PerceptionPipelineSystem()

        # Patch __getitem__ for pipeline crop
        # We assume pipeline crops 400x400
        original_getitem = np.ndarray.__getitem__
        np.ndarray.__getitem__ = MagicMock(return_value=np.zeros((400, 400, 3)))

        try:
            await system.update(world, 0.1)
        finally:
            np.ndarray.__getitem__ = original_getitem

        # Check output
        assert comp.get_observation("center_crop") is not None
        assert comp.get_observation("grayscale_view") is not None

    asyncio.run(_test())

def test_sensory_input():
    async def _test():
        # mss is mocked in sys.modules, so import mss works.
        # But SensoryInputSystem does: self.sct = mss.mss() if mss else None
        # We need to ensure mss.mss() returns a mock with monitors and grab

        import mss as mss_mod
        mock_sct = MagicMock()
        mock_sct.monitors = [{"top":0, "left":0, "width":100, "height":100}, {"top":0, "left":0, "width":100, "height":100}]
        mock_sct.grab.return_value = np.zeros((100, 100, 4))
        mss_mod.mss = MagicMock(return_value=mock_sct)

        world = World()
        entity = world.create_entity()
        comp = PerceptionComponent()
        world.add_component(entity, comp)

        system = SensoryInputSystem()
        await system.update(world, 0.1)

        obs = comp.get_observation("raw_screen")
        assert obs is not None
        assert obs.content.shape == (100, 100, 4)

    asyncio.run(_test())

def test_action_execution():
    async def _test():
        # PyAutoGUI mocked via sys.modules
        import pyautogui as pag

        world = World()
        entity = world.create_entity()
        buffer = ActionBufferComponent()
        world.add_component(entity, buffer)

        action = ClickAction(x=10, y=20)
        buffer.enqueue(action)

        system = ActionExecutionSystem()
        await system.update(world, 0.1)

        assert len(buffer.action_queue) == 0
        pag.click.assert_called()

    asyncio.run(_test())
