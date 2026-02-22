import asyncio
from typing import Dict, List, Set, Any
import uuid

from core.system import System
from core.world import World
from core.entity import Entity
from components.core import MailboxComponent, Message

class MessageRouterSystem(System):
    """
    Orchestrates message passing between agents (Pub/Sub + Direct).
    Run this at the BEGINNING of the tick (Phase 1).
    """

    async def update(self, world: World, dt: float):
        # 1. Collect all outgoing messages from all agents
        all_outboxes: List[Message] = []

        # In a real implementation we would iterate efficiently
        # Since we don't have a direct "get all components" iterator in World yet
        # We use get_entities_with

        entities_with_mailbox = world.get_entities_with(MailboxComponent)

        # Temporary storage for broadcast topics -> subscribers
        # topic -> set of Entity IDs
        topic_subscribers: Dict[str, Set[Entity]] = {}

        # First pass: Build subscriber map and collect outboxes
        for entity in entities_with_mailbox:
            mailbox = world.get_component(entity, MailboxComponent)

            # Map subscriptions
            for topic in mailbox.subscriptions:
                if topic not in topic_subscribers:
                    topic_subscribers[topic] = set()
                topic_subscribers[topic].add(entity)

            # Collect messages
            if mailbox.outbox:
                all_outboxes.extend(mailbox.outbox)
                mailbox.outbox.clear() # Clear outbox after collection

        # 2. Route messages
        for message in all_outboxes:
            # Case A: Direct Message
            if message.target_id:
                target_entity = message.target_id
                target_mailbox = world.get_component(target_entity, MailboxComponent)
                if target_mailbox:
                    # Deep copy to ensure isolation if sender modifies original later (unlikely but safe)
                    target_mailbox.inbox.append(message.model_copy(deep=True))
                else:
                    print(f"Message dropped: Target {target_entity} not found or has no mailbox.")

            # Case B: Broadcast (Pub/Sub)
            else:
                topic = message.topic
                if topic in topic_subscribers:
                    subscribers = topic_subscribers[topic]
                    for sub_entity in subscribers:
                        if sub_entity == message.sender_id:
                            continue

                        sub_mailbox = world.get_component(sub_entity, MailboxComponent)
                        if sub_mailbox:
                            # Deep copy CRITICAL for broadcast to prevent shared state bugs
                            sub_mailbox.inbox.append(message.model_copy(deep=True))
