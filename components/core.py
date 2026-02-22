from pydantic import BaseModel, Field
from typing import Dict, List, Any
import uuid
from core.component import BaseComponent

class AgentMetaComponent(BaseComponent):
    """Agent identity: Name, role, status"""
    name: str = "Agent_01"
    role: str = "Scraper" # Parser, Warrior, Analyst
    status: str = "IDLE" # ACTIVE, ERROR, WAITING

class Message(BaseModel):
    """Unit of information exchange between agents"""
    sender_id: uuid.UUID
    target_id: uuid.UUID | None = None # If None — Broadcast
    topic: str # e.g.: "price_drop", "enemy_spotted"
    payload: Dict[str, Any] # The data itself (JSON)

class MailboxComponent(BaseComponent):
    """Mailbox for Pub/Sub architecture"""
    inbox: List[Message] = Field(default_factory=list)
    outbox: List[Message] = Field(default_factory=list)
    subscriptions: List[str] = Field(default_factory=list) # Topics the agent is subscribed to

class MemoryComponent(BaseComponent):
    """Working and episodic memory (Blackboard)"""
    blackboard: Dict[str, Any] = Field(default_factory=dict)
    history: List[str] = Field(default_factory=list) # Log of last actions for LLM (episodic_log)

class ActionBufferComponent(BaseComponent):
    """Execution queue"""
    queue: List[Any] = Field(default_factory=list) # List of BaseAction objects
    current_action_status: str = "IDLE"

class PerceptionComponent(BaseComponent):
    """Ephemeral snapshot of the world (updated every tick)"""
    visible_entities: List[dict] = Field(default_factory=list) # What we see right now
    raw_context: Dict[str, Any] = Field(default_factory=dict) # Parsed JSON goes here
    raw_frame_id: str | None = None

class BrainComponent(BaseComponent):
    status: str = "IDLE" # IDLE, RUNNING_BT, WAITING_LLM
    context: Dict[str, Any] = Field(default_factory=dict)
