from typing import List, Optional
try:
    from pydantic import Field
except ImportError:
    from serpentine.utils.pydantic_utils import Field

from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry
from serpentine.core.messages import SwarmMessage

@Registry.register_component
class AgentMetaComponent(BaseComponent):
    """
    Metadata for agents in the swarm.
    """
    role: str = "worker"
    status: str = "idle"
    agent_name: str = "Agent"

@Registry.register_component
class MailboxComponent(BaseComponent):
    """
    Stores incoming and outgoing messages for inter-agent communication.
    """
    inbox: List[SwarmMessage] = Field(default_factory=list)
    outbox: List[SwarmMessage] = Field(default_factory=list)

    # Optional: message history or log could be added later for persistence
