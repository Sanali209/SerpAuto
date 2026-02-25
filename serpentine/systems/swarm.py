import time
from typing import List

from serpentine.systems.base import System
from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.core.world import World
from serpentine.components.swarm import MailboxComponent, AgentMetaComponent
from serpentine.utils.logging import configure_logging

logger = configure_logging()

@Registry.register_system(phase=SystemPhase.MAIL_ROUTING, modes=[EngineMode.ARCHITECT, EngineMode.PRODUCTION, EngineMode.TEACHER, EngineMode.GYMNASIUM, EngineMode.CONTINUOUS_LEARNING])
class MessageRouterSystem(System):
    """
    Routes messages between agents based on MailboxComponent.
    Handles point-to-point and broadcast messaging.
    """

    async def update(self, world: World, dt: float) -> None:
        # Get all mailboxes
        mailboxes = world.get_components(MailboxComponent)
        if not mailboxes:
            return

        current_time = time.time()

        # We need to collect messages first to avoid modifying mailboxes while iterating if we were doing something complex,
        # but here we are modifying lists inside components, which is fine as long as we don't add/remove components from world.

        # However, for broadcast, we need to iterate all mailboxes again.
        # So having a reference `mailboxes` dict is good.

        for entity_id, mailbox in mailboxes.items():
            if not mailbox.outbox:
                continue

            # Process outbox
            # We iterate a copy of the list so we can modify the original
            for message in list(mailbox.outbox):
                # Check TTL
                if current_time - message.timestamp > message.ttl:
                    logger.debug(f"Message {message.topic} expired (TTL). Dropping.")
                    mailbox.outbox.remove(message)
                    continue

                # Route message
                if message.recipient_id:
                    # Point-to-point
                    target_mailbox = world.get_component(message.recipient_id, MailboxComponent)
                    if target_mailbox:
                        target_mailbox.inbox.append(message)
                        logger.debug(f"Message {message.topic} routed from {message.sender_id} to {message.recipient_id}")
                    else:
                        logger.warning(f"Target {message.recipient_id} has no mailbox. Message dropped.")
                else:
                    # Broadcast
                    # Send to all entities with MailboxComponent EXCEPT sender
                    count = 0
                    for target_id, target_mb in mailboxes.items():
                        if target_id != message.sender_id:
                            target_mb.inbox.append(message)
                            count += 1
                    logger.debug(f"Message {message.topic} broadcast from {message.sender_id} to {count} agents")

                # Remove from outbox after routing
                mailbox.outbox.remove(message)
