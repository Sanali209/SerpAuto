import unittest
import uuid
from core.world import World
from core.registry import COMPONENT_REGISTRY
from components.core import AgentMetaComponent, MemoryComponent
from components.spatial import TransformComponent

class TestPersistence(unittest.TestCase):
    def test_serialization_cycle(self):
        """Test full save/load cycle of the World"""
        original_world = World()

        # 1. Create entities with various components
        agent = original_world.add_entity()
        original_world.add_component(agent, AgentMetaComponent(name="TestAgent", role="Tester"))
        original_world.add_component(agent, TransformComponent(x=10.5, y=20.0))

        box = original_world.add_entity()
        original_world.add_component(box, TransformComponent(x=50.0, y=50.0))

        # 2. Serialize
        data = original_world.serialize()

        # Verify structure
        self.assertIsInstance(data, dict)
        self.assertIn("entities", data)
        self.assertIn("components", data)
        self.assertEqual(len(data["entities"]), 2)
        self.assertIn("AgentMetaComponent", data["components"])
        self.assertIn("TransformComponent", data["components"])

        # 3. Deserialize into NEW world
        new_world = World()
        new_world.deserialize(data, COMPONENT_REGISTRY)

        # 4. Verify Integrity
        # Entity count
        self.assertEqual(len(new_world._entities), 2)

        # Component values
        # We need to find the agent entity ID in the new world (it should be the same UUID)
        restored_agent_meta = new_world.get_component(agent, AgentMetaComponent)
        self.assertIsNotNone(restored_agent_meta)
        self.assertEqual(restored_agent_meta.name, "TestAgent")
        self.assertEqual(restored_agent_meta.role, "Tester")

        restored_agent_transform = new_world.get_component(agent, TransformComponent)
        self.assertIsNotNone(restored_agent_transform)
        self.assertEqual(restored_agent_transform.x, 10.5)

        restored_box_transform = new_world.get_component(box, TransformComponent)
        self.assertIsNotNone(restored_box_transform)
        self.assertEqual(restored_box_transform.x, 50.0)

    def test_deserialize_clears_old_state(self):
        """Ensure loading a snapshot wipes the previous state"""
        world = World()
        world.add_entity() # Add a dummy entity

        empty_snapshot = {"entities": [], "components": {}}

        world.deserialize(empty_snapshot, COMPONENT_REGISTRY)
        self.assertEqual(len(world._entities), 0)

if __name__ == '__main__':
    unittest.main()
