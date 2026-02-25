import sys
from unittest.mock import MagicMock

# Mock dependencies
try:
    import numpy as np
except ImportError:
    np = MagicMock()
    sys.modules["numpy"] = np

try:
    import cv2
except ImportError:
    cv2 = MagicMock()
    sys.modules["cv2"] = cv2

try:
    import mss
except ImportError:
    mss = MagicMock()
    sys.modules["mss"] = mss

try:
    import pyautogui
except ImportError:
    pyautogui = MagicMock()
    sys.modules["pyautogui"] = pyautogui

import unittest
import asyncio
from typing import Any

from serpentine.mind.core import BehaviorTreeNode, Status, Blackboard
from serpentine.mind.composites import Sequence, Selector, Parallel
from serpentine.mind.decorators import Inverter, Succeeder, RepeatUntilFail
from serpentine.mind.actions import WaitNode, SetBlackboardVariable
from serpentine.mind.brain import BrainComponent

class MockNode(BehaviorTreeNode):
    def __init__(self, status: Status):
        super().__init__()
        self.desired_status = status
        self.tick_count = 0

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        self.tick_count += 1
        return self.desired_status

class MockRunningNode(BehaviorTreeNode):
    def __init__(self, run_ticks: int, final_status: Status):
        super().__init__()
        self.run_ticks = run_ticks
        self.final_status = final_status
        self.ticks = 0

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        self.ticks += 1
        if self.ticks <= self.run_ticks:
            return Status.RUNNING
        return self.final_status

    def reset(self):
        self.ticks = 0

class TestMindBT(unittest.IsolatedAsyncioTestCase):
    async def test_blackboard(self):
        bb = Blackboard()
        bb.set("key", "value")
        self.assertEqual(bb.get("key"), "value")
        self.assertTrue(bb.has("key"))
        bb.clear()
        self.assertFalse(bb.has("key"))

    async def test_sequence_success(self):
        child1 = MockNode(Status.SUCCESS)
        child2 = MockNode(Status.SUCCESS)
        seq = Sequence([child1, child2])

        status = await seq.tick(None, None, Blackboard())
        self.assertEqual(status, Status.SUCCESS)
        self.assertEqual(child1.tick_count, 1)
        self.assertEqual(child2.tick_count, 1)

    async def test_sequence_failure(self):
        child1 = MockNode(Status.SUCCESS)
        child2 = MockNode(Status.FAILURE)
        child3 = MockNode(Status.SUCCESS)
        seq = Sequence([child1, child2, child3])

        status = await seq.tick(None, None, Blackboard())
        self.assertEqual(status, Status.FAILURE)
        self.assertEqual(child1.tick_count, 1)
        self.assertEqual(child2.tick_count, 1)
        self.assertEqual(child3.tick_count, 0)

    async def test_sequence_running(self):
        child1 = MockNode(Status.SUCCESS)
        child2 = MockRunningNode(run_ticks=1, final_status=Status.SUCCESS)
        seq = Sequence([child1, child2])

        # Tick 1: Child 1 success, Child 2 running
        status = await seq.tick(None, None, Blackboard())
        self.assertEqual(status, Status.RUNNING)

        # Tick 2: Child 2 success
        status = await seq.tick(None, None, Blackboard())
        self.assertEqual(status, Status.SUCCESS)

    async def test_selector_success(self):
        child1 = MockNode(Status.FAILURE)
        child2 = MockNode(Status.SUCCESS)
        sel = Selector([child1, child2])

        status = await sel.tick(None, None, Blackboard())
        self.assertEqual(status, Status.SUCCESS)
        self.assertEqual(child1.tick_count, 1)
        self.assertEqual(child2.tick_count, 1)

    async def test_selector_failure(self):
        child1 = MockNode(Status.FAILURE)
        child2 = MockNode(Status.FAILURE)
        sel = Selector([child1, child2])

        status = await sel.tick(None, None, Blackboard())
        self.assertEqual(status, Status.FAILURE)

    async def test_inverter(self):
        node = Inverter(MockNode(Status.SUCCESS))
        status = await node.tick(None, None, Blackboard())
        self.assertEqual(status, Status.FAILURE)

        node = Inverter(MockNode(Status.FAILURE))
        status = await node.tick(None, None, Blackboard())
        self.assertEqual(status, Status.SUCCESS)

    async def test_wait_node(self):
        node = WaitNode(duration=0.1)

        # Tick 1: Starts running
        status = await node.tick(None, None, Blackboard())
        self.assertEqual(status, Status.RUNNING)

        await asyncio.sleep(0.15)

        # Tick 2: Should be done
        status = await node.tick(None, None, Blackboard())
        self.assertEqual(status, Status.SUCCESS)

    async def test_wait_node_reentry(self):
        node = WaitNode(duration=0.1)

        # Run once
        await node.tick(None, None, Blackboard())
        await asyncio.sleep(0.15)
        status = await node.tick(None, None, Blackboard())
        self.assertEqual(status, Status.SUCCESS)

        # Reset and run again
        node.reset()
        status = await node.tick(None, None, Blackboard())
        self.assertEqual(status, Status.RUNNING)

    async def test_set_blackboard(self):
        bb = Blackboard()
        node = SetBlackboardVariable("test", 123)
        await node.tick(None, None, bb)
        self.assertEqual(bb.get("test"), 123)

if __name__ == '__main__':
    unittest.main()
