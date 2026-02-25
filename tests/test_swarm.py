import unittest
import asyncio
from uuid import uuid4
import time

from serpentine.core.world import World
from serpentine.core.entity import EntityID
from serpentine.core.messages import SwarmMessage
from serpentine.components.swarm import MailboxComponent, AgentMetaComponent
from serpentine.systems.swarm import MessageRouterSystem
from serpentine.mind.swarm_nodes import SendMessageNode, ListenForEventNode
from serpentine.mind.core import Blackboard, Status

class TestSwarmSystem(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.world = World()
        self.router = MessageRouterSystem()

        # Create Entity 1 (Sender)
        self.entity1 = self.world.create_entity()
        self.world.add_component(self.entity1, MailboxComponent())
        self.world.add_component(self.entity1, AgentMetaComponent(agent_name="Agent1"))

        # Create Entity 2 (Receiver)
        self.entity2 = self.world.create_entity()
        self.world.add_component(self.entity2, MailboxComponent())
        self.world.add_component(self.entity2, AgentMetaComponent(agent_name="Agent2"))

    async def test_point_to_point_message(self):
        mailbox1 = self.world.get_component(self.entity1, MailboxComponent)
        mailbox2 = self.world.get_component(self.entity2, MailboxComponent)

        # Create message
        msg = SwarmMessage(
            sender_id=self.entity1,
            recipient_id=self.entity2,
            topic="test_topic",
            payload={"data": "hello"}
        )
        mailbox1.outbox.append(msg)

        # Run router
        await self.router.update(self.world, 0.1)

        # Verify delivery
        self.assertEqual(len(mailbox1.outbox), 0)
        self.assertEqual(len(mailbox2.inbox), 1)
        self.assertEqual(mailbox2.inbox[0].payload["data"], "hello")
        self.assertEqual(mailbox2.inbox[0].sender_id, self.entity1)

    async def test_broadcast_message(self):
        mailbox1 = self.world.get_component(self.entity1, MailboxComponent)
        mailbox2 = self.world.get_component(self.entity2, MailboxComponent)

        # Create broadcast message
        msg = SwarmMessage(
            sender_id=self.entity1,
            recipient_id=None,
            topic="broadcast_topic",
            payload={"info": "everyone"}
        )
        mailbox1.outbox.append(msg)

        # Run router
        await self.router.update(self.world, 0.1)

        # Verify delivery to Entity 2
        self.assertEqual(len(mailbox1.outbox), 0)
        self.assertEqual(len(mailbox2.inbox), 1)
        self.assertEqual(mailbox2.inbox[0].payload["info"], "everyone")

        # Verify sender (Entity 1) did NOT receive it (standard logic usually excludes sender)
        # My implementation excludes sender.
        self.assertEqual(len(mailbox1.inbox), 0)

    async def test_ttl_expiry(self):
        mailbox1 = self.world.get_component(self.entity1, MailboxComponent)

        # Create message with short TTL
        msg = SwarmMessage(
            sender_id=self.entity1,
            recipient_id=self.entity2,
            topic="expire_topic",
            payload={},
            ttl=0.1
        )
        # Manually set timestamp to past
        msg.timestamp = time.time() - 1.0

        mailbox1.outbox.append(msg)

        # Run router
        await self.router.update(self.world, 0.1)

        # Verify dropped
        self.assertEqual(len(mailbox1.outbox), 0)
        mailbox2 = self.world.get_component(self.entity2, MailboxComponent)
        self.assertEqual(len(mailbox2.inbox), 0)

    async def test_send_message_node(self):
        node = SendMessageNode()
        node.params.recipient_id = self.entity2
        node.params.topic = "node_topic"
        node.params.payload = {"from": "node"}

        blackboard = Blackboard()
        status = await node.tick(self.world, self.entity1, blackboard)

        self.assertEqual(status, Status.SUCCESS)

        mailbox1 = self.world.get_component(self.entity1, MailboxComponent)
        self.assertEqual(len(mailbox1.outbox), 1)
        self.assertEqual(mailbox1.outbox[0].topic, "node_topic")
        self.assertEqual(mailbox1.outbox[0].recipient_id, self.entity2)

    async def test_listen_for_event_node(self):
        mailbox2 = self.world.get_component(self.entity2, MailboxComponent)

        # Inject message
        msg = SwarmMessage(
            sender_id=self.entity1,
            recipient_id=self.entity2,
            topic="listen_topic",
            payload={"secret": 123}
        )
        mailbox2.inbox.append(msg)

        node = ListenForEventNode(params=ListenForEventNode.Params(topic="listen_topic", output_key="received_data"))

        blackboard = Blackboard()
        status = await node.tick(self.world, self.entity2, blackboard)

        self.assertEqual(status, Status.SUCCESS)
        self.assertEqual(len(mailbox2.inbox), 0)
        self.assertTrue(blackboard.has("received_data"))
        self.assertEqual(blackboard.get("received_data")["secret"], 123)

        # Test subsequent failure (inbox empty)
        status = await node.tick(self.world, self.entity2, blackboard)
        self.assertEqual(status, Status.FAILURE)

if __name__ == "__main__":
    unittest.main()
