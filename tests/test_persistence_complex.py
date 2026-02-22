import unittest
import uuid
import json
from core.world import World
from core.registry import COMPONENT_REGISTRY
from components.core import MailboxComponent, Message

class TestComplexPersistence(unittest.TestCase):
    def test_serialize_uuid_fields(self):
        """Test that components with UUID fields (like MailboxComponent) serialize correctly."""
        world = World()
        agent_a = world.add_entity()
        agent_b = world.add_entity()

        # Create a Mailbox with a Message containing UUIDs
        mailbox = MailboxComponent()
        msg = Message(
            sender_id=agent_a,
            target_id=agent_b,
            topic="test_topic",
            payload={"foo": "bar"}
        )
        mailbox.outbox.append(msg)

        world.add_component(agent_a, mailbox)

        # This call would fail if mode='json' wasn't used in model_dump
        try:
            json_dump = world.serialize()
        except TypeError as e:
            self.fail(f"Serialization failed likely due to UUID: {e}")

        # Verify Deserialize works too
        new_world = World()
        new_world.deserialize(json_dump, COMPONENT_REGISTRY)

        restored_mailbox = new_world.get_component(agent_a, MailboxComponent)
        self.assertIsNotNone(restored_mailbox)
        self.assertEqual(len(restored_mailbox.outbox), 1)
        self.assertEqual(restored_mailbox.outbox[0].sender_id, agent_a)
        self.assertEqual(restored_mailbox.outbox[0].target_id, agent_b)

if __name__ == '__main__':
    unittest.main()
