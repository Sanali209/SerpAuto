import unittest
import asyncio
from core.world import World
from core.engine_v2 import Phase
from components.core import BrainComponent, PerceptionComponent, ActionBufferComponent, RewardComponent
from systems.action import ActionExecutionSystem
from systems.perception import SensoryInputSystem

class MockAction:
    def __init__(self):
        self.target_env = "EXTERNAL_OS"
    async def execute(self):
        return "SUCCESS"

class TestActorLearner(unittest.IsolatedAsyncioTestCase):
    async def test_io_lock_lifecycle(self):
        world = World()
        entity = "agent_01"
        
        brain = BrainComponent()
        perception = PerceptionComponent()
        action_buffer = ActionBufferComponent()
        
        world.add_component(entity, brain)
        world.add_component(entity, perception)
        world.add_component(entity, action_buffer)
        
        action_sys = ActionExecutionSystem()
        sensory_sys = SensoryInputSystem()
        
        # 1. Trigger an external action
        action_buffer.queue.append(MockAction())
        await action_sys.update(world, 0.1)
        
        self.assertEqual(brain.status, "WAITING_FOR_IO")
        
        # 2. Capture a new frame
        await sensory_sys.update(world, 0.1)
        
        self.assertEqual(brain.status, "READY_TO_LEARN")

if __name__ == '__main__':
    unittest.main()
