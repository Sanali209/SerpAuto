from typing import Any, Dict, Optional
try:
    from pydantic import BaseModel, Field
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, Field

from serpentine.mind.core import BehaviorTreeNode, Blackboard, Status
from serpentine.core.registry import Registry
from serpentine.components.swarm import MailboxComponent
from serpentine.core.messages import SwarmMessage
from serpentine.core.entity import EntityID
from serpentine.core.world import World

@Registry.register_node(category="Swarm", icon="📨", description="Sends a message to another agent or broadcasts.")
class SendMessageNode(BehaviorTreeNode):
    class Params(BaseModel):
        recipient_id: Optional[EntityID] = None  # Static recipient (None = broadcast)
        recipient_key: Optional[str] = None      # Dynamic recipient from blackboard
        topic: str = "default"
        payload: Dict[str, Any] = Field(default_factory=dict) # Static payload
        payload_key: Optional[str] = None        # Dynamic payload from blackboard

    async def tick(self, world: World, entity: EntityID, blackboard: Blackboard) -> Status:
        mailbox = world.get_component(entity, MailboxComponent)
        if not mailbox:
            return Status.FAILURE

        # Determine recipient
        recipient = self.params.recipient_id
        if self.params.recipient_key and blackboard.has(self.params.recipient_key):
            recipient = blackboard.get(self.params.recipient_key)

        # Determine payload
        payload = self.params.payload
        if self.params.payload_key and blackboard.has(self.params.payload_key):
            payload = blackboard.get(self.params.payload_key)

        # Create message
        message = SwarmMessage(
            sender_id=entity,
            recipient_id=recipient,
            topic=self.params.topic,
            payload=payload
        )

        mailbox.outbox.append(message)
        return Status.SUCCESS

@Registry.register_node(category="Swarm", icon="👂", description="Listens for a message with a specific topic.")
class ListenForEventNode(BehaviorTreeNode):
    class Params(BaseModel):
        topic: str
        output_key: str = "event_payload"  # Where to store the payload in blackboard

    async def tick(self, world: World, entity: EntityID, blackboard: Blackboard) -> Status:
        mailbox = world.get_component(entity, MailboxComponent)
        if not mailbox:
            return Status.FAILURE

        # Check inbox for matching topic
        # Iterate copy to modify list safely if needed (though pop is safer)
        # We want to find the first matching message and consume it.

        found_message = None
        for message in mailbox.inbox:
            if message.topic == self.params.topic:
                found_message = message
                break

        if found_message:
            mailbox.inbox.remove(found_message)
            blackboard.set(self.params.output_key, found_message.payload)
            return Status.SUCCESS

        return Status.FAILURE
