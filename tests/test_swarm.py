import unittest
import asyncio
import uuid
from typing import Dict, Any, List

from core.world import World
from core.component import BaseComponent
from core.entity import Entity
from components.core import MailboxComponent, Message, MemoryComponent
from systems.swarm import MessageRouterSystem
from brain.behavior_tree import SendMessageNode, ListenForEventNode, Status

class TestSwarm(unittest.TestCase):
    def test_message_routing_isolation(self):
        """Test that broadcast messages are isolated via deep copy"""
        world = World()

        agent_a = world.add_entity()
        agent_b = world.add_entity()
        agent_c = world.add_entity()

        # Init mailboxes
        mb_a = MailboxComponent(subscriptions=[])
        mb_b = MailboxComponent(subscriptions=["topic_iso"])
        mb_c = MailboxComponent(subscriptions=["topic_iso"])

        world.add_component(agent_a, mb_a)
        world.add_component(agent_b, mb_b)
        world.add_component(agent_c, mb_c)

        # A sends message to topic_iso
        original_payload = {"count": 1, "nested": {"a": 1}}
        msg = Message(
            sender_id=agent_a,
            topic="topic_iso",
            payload=original_payload
        )
        mb_a.outbox.append(msg)

        # Run system
        system = MessageRouterSystem()
        asyncio.run(system.update(world, 0.1))

        # Verify B and C got it
        self.assertEqual(len(mb_b.inbox), 1)
        self.assertEqual(len(mb_c.inbox), 1)

        # Modify B's payload
        mb_b.inbox[0].payload["count"] = 999
        mb_b.inbox[0].payload["nested"]["a"] = 999

        # Verify C's payload is UNCHANGED (Isolation Check)
        self.assertEqual(mb_c.inbox[0].payload["count"], 1)
        self.assertEqual(mb_c.inbox[0].payload["nested"]["a"], 1)

    def test_bt_nodes_integration(self):
        """Test SendMessageNode and ListenForEventNode interaction"""
        world = World()
        agent = world.add_entity()

        # Setup components
        mem = MemoryComponent()
        mb = MailboxComponent(subscriptions=[])
        world.add_component(agent, mem)
        world.add_component(agent, mb)

        # 1. Test SendMessageNode
        mem.blackboard["deal_data"] = {"price": 100}
        send_node = SendMessageNode(topic="deals", payload_key="deal_data")

        status = asyncio.run(send_node.tick(world, agent))
        self.assertEqual(status, Status.SUCCESS)
        self.assertEqual(len(mb.outbox), 1)
        self.assertEqual(mb.outbox[0].topic, "deals")
        self.assertEqual(mb.outbox[0].payload["price"], 100)

        # 2. Simulate MessageRouter (Manually move from outbox to inbox for test)
        msg = mb.outbox.pop(0)
        mb.inbox.append(msg)

        # 3. Test ListenForEventNode
        listen_node = ListenForEventNode(topic="deals", output_key="received_deal")

        status = asyncio.run(listen_node.tick(world, agent))
        self.assertEqual(status, Status.SUCCESS)
        self.assertEqual(len(mb.inbox), 0) # Should be consumed
        self.assertEqual(mem.blackboard["received_deal"]["price"], 100)

        # Test Listen Failure (Empty Inbox)
        status = asyncio.run(listen_node.tick(world, agent))
        self.assertEqual(status, Status.FAILURE)

if __name__ == '__main__':
    unittest.main()
