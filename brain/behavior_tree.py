from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional
import asyncio
from core.world import World
from core.entity import Entity
from components.core import MailboxComponent, Message, MemoryComponent

class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"

class BehaviorTreeNode(ABC):
    @abstractmethod
    async def tick(self, world: World, agent_id: Entity) -> Status:
        pass

# --- Control Flow Nodes ---

class Selector(BehaviorTreeNode):
    """Fallback node: Runs children until one succeeds."""
    def __init__(self, children: List[BehaviorTreeNode]):
        self.children = children

    async def tick(self, world: World, agent_id: Entity) -> Status:
        for child in self.children:
            status = await child.tick(world, agent_id)
            if status != Status.FAILURE:
                return status
        return Status.FAILURE

class Sequence(BehaviorTreeNode):
    """Sequence node: Runs children until one fails."""
    def __init__(self, children: List[BehaviorTreeNode]):
        self.children = children

    async def tick(self, world: World, agent_id: Entity) -> Status:
        for child in self.children:
            status = await child.tick(world, agent_id)
            if status != Status.SUCCESS:
                return status
        return Status.SUCCESS

class Parallel(BehaviorTreeNode):
    """
    Runs all children concurrently.
    Policy 'ALL_SUCCESS' (Sequence-like) or 'ONE_SUCCESS' (Selector-like).
    """
    def __init__(self, children: List[BehaviorTreeNode], policy: str = "ALL_SUCCESS"):
        self.children = children
        self.policy = policy

    async def tick(self, world: World, agent_id: Entity) -> Status:
        # Run all children concurrently
        results = await asyncio.gather(*[child.tick(world, agent_id) for child in self.children])

        if self.policy == "ALL_SUCCESS":
            if any(r == Status.FAILURE for r in results):
                return Status.FAILURE
            if any(r == Status.RUNNING for r in results):
                return Status.RUNNING
            return Status.SUCCESS

        elif self.policy == "ONE_SUCCESS":
            if any(r == Status.SUCCESS for r in results):
                return Status.SUCCESS
            if any(r == Status.RUNNING for r in results):
                return Status.RUNNING
            return Status.FAILURE

        return Status.FAILURE

# --- MAS Communication Nodes ---

class SendMessageNode(BehaviorTreeNode):
    """
    Constructs a message from Blackboard data and puts it in the Outbox.
    Example: topic="deal_found", payload_key="current_deal"
    """
    def __init__(self, topic: str, payload_key: str, target_id_key: Optional[str] = None):
        self.topic = topic
        self.payload_key = payload_key
        self.target_id_key = target_id_key

    async def tick(self, world: World, agent_id: Entity) -> Status:
        memory = world.get_component(agent_id, MemoryComponent)
        mailbox = world.get_component(agent_id, MailboxComponent)

        if not memory or not mailbox:
            return Status.FAILURE

        # Get payload from blackboard
        payload = memory.blackboard.get(self.payload_key)
        if payload is None:
            # Cannot send message without data
            return Status.FAILURE

        # Get optional target ID
        target_id = None
        if self.target_id_key:
            target_id = memory.blackboard.get(self.target_id_key)

        # Create Message
        msg = Message(
            sender_id=agent_id,
            target_id=target_id,
            topic=self.topic,
            payload=payload
        )

        mailbox.outbox.append(msg)
        return Status.SUCCESS

class ListenForEventNode(BehaviorTreeNode):
    """
    Checks Inbox for a specific topic. If found, extracts payload to Blackboard.
    Returns SUCCESS if message found, FAILURE otherwise (acts as a Guard).
    """
    def __init__(self, topic: str, output_key: str):
        self.topic = topic
        self.output_key = output_key

    async def tick(self, world: World, agent_id: Entity) -> Status:
        mailbox = world.get_component(agent_id, MailboxComponent)
        memory = world.get_component(agent_id, MemoryComponent)

        if not mailbox or not memory:
            return Status.FAILURE

        # Check inbox for the first message with matching topic
        found_msg = None
        found_index = -1

        for i, msg in enumerate(mailbox.inbox):
            if msg.topic == self.topic:
                found_msg = msg
                found_index = i
                break

        if found_msg:
            # Extract payload to Blackboard
            memory.blackboard[self.output_key] = found_msg.payload

            # Consume message (remove from inbox)
            mailbox.inbox.pop(found_index)

            return Status.SUCCESS

        return Status.FAILURE
