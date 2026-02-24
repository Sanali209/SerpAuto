from pydantic import BaseModel, Field
from typing import Dict, List, Any
import uuid
from core.component import BaseComponent
from core.registry import register_component

@register_component()
class MetadataComponent(BaseComponent):
    """Generic entity metadata: Human-readable name, tags, etc."""
    name: str = "New Entity"
    tags: List[str] = Field(default_factory=list)
    color: List[float] = [1.0, 1.0, 1.0, 1.0] # For GUI highlighting

class Message(BaseModel):
    """Unit of information exchange between agents"""
    sender_id: uuid.UUID
    target_id: uuid.UUID | None = None # If None — Broadcast
    topic: str # e.g.: "price_drop", "enemy_spotted"
    payload: Dict[str, Any] # The data itself (JSON)

@register_component()
class MailboxComponent(BaseComponent):
    """Mailbox for Pub/Sub architecture"""
    inbox: List[Message] = Field(default_factory=list)
    outbox: List[Message] = Field(default_factory=list)
    subscriptions: List[str] = Field(default_factory=list) # Topics the agent is subscribed to

@register_component()
class MemoryComponent(BaseComponent):
    """Working and episodic memory (Blackboard)"""
    blackboard: Dict[str, Any] = Field(default_factory=dict)
    history: List[str] = Field(default_factory=list) # Log of last actions for LLM (episodic_log)

@register_component()
class ActionBufferComponent(BaseComponent):
    """Execution queue"""
    queue: List[Any] = Field(default_factory=list) # List of BaseAction objects
    current_action_status: str = "IDLE"

@register_component()
class PerceptionComponent(BaseComponent):
    """Ephemeral snapshot of the world (updated every tick)"""
    visible_entities: List[dict] = Field(default_factory=list) # What we see right now
    raw_context: Dict[str, Any] = Field(default_factory=dict) # Parsed JSON goes here
    raw_frame_id: str | None = None
    processed_frame: Any = Field(default=None, exclude=True) # np.ndarray for visual debugging

@register_component()
class BrainComponent(BaseComponent):
    status: str = "IDLE" # IDLE, THINKING, WAITING_FOR_IO, READY_TO_LEARN
    context: Dict[str, Any] = Field(default_factory=dict)
    bt_root: Any = Field(default=None, exclude=True) # Live BehaviorTreeNode instance
    last_state: Any = None  # Запоминаем S_t
    last_action: Any = None # Запоминаем A_t

@register_component()
class MeshComponent(BaseComponent):
    """3D geometry reference (VAO/VBO data)"""
    model_path: str = "assets/models/cube.obj"
    vao_id: str | None = None

@register_component()
class MaterialComponent(BaseComponent):
    """Shader properties and textures"""
    diffuse_color: List[float] = [1.0, 1.0, 1.0, 1.0]
    shader_name: str = "default_lit"
    texture_path: str | None = None

@register_component()
class CameraComponent(BaseComponent):
    """View and Projection matrices for rendering"""
    is_active: bool = True
    fov: float = 45.0
    near: float = 0.1
    far: float = 1000.0

@register_component()
class PlayerControllerComponent(BaseComponent):
    """Tag to identify the human-controlled entity"""
    is_active: bool = True

@register_component()
class RewardComponent(BaseComponent):
    """State of rewards for Reinforcement Learning"""
    current_reward: float = 0.0
    cumulative_reward: float = 0.0
    total_score: float = 0.0
    is_terminated: bool = False
    is_truncated: bool = False
