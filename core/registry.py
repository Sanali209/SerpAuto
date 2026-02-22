# Helper to register all components for deserialization
from typing import Type, Dict
from core.component import BaseComponent
from components.core import (
    AgentMetaComponent, MailboxComponent, MemoryComponent,
    ActionBufferComponent, PerceptionComponent, BrainComponent
)
from components.spatial import TransformComponent, SpatialGridComponent, UIElementComponent
from components.web import WebSessionComponent, DOMNodeComponent, PayloadExtractionComponent
from components.domain import StatsComponent, InventoryComponent
from components.internal import VelocityComponent, ColliderComponent, SpriteComponent, RewardComponent

COMPONENT_REGISTRY: Dict[str, Type[BaseComponent]] = {
    "AgentMetaComponent": AgentMetaComponent,
    "MailboxComponent": MailboxComponent,
    "MemoryComponent": MemoryComponent,
    "ActionBufferComponent": ActionBufferComponent,
    "PerceptionComponent": PerceptionComponent,
    "BrainComponent": BrainComponent,
    "TransformComponent": TransformComponent,
    "SpatialGridComponent": SpatialGridComponent,
    "UIElementComponent": UIElementComponent,
    "WebSessionComponent": WebSessionComponent,
    "DOMNodeComponent": DOMNodeComponent,
    "PayloadExtractionComponent": PayloadExtractionComponent,
    "StatsComponent": StatsComponent,
    "InventoryComponent": InventoryComponent,
    "VelocityComponent": VelocityComponent,
    "ColliderComponent": ColliderComponent,
    "SpriteComponent": SpriteComponent,
    "RewardComponent": RewardComponent,
}
