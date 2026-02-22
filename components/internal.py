from typing import List, Literal
from core.component import BaseComponent
from core.registry import register_component

@register_component()
class VelocityComponent(BaseComponent):
    """Vector velocity for internal physics"""
    vx: float = 0.0
    vy: float = 0.0

@register_component()
class ColliderComponent(BaseComponent):
    """Geometry for collision detection"""
    shape: Literal["BOX", "CIRCLE"] = "BOX"
    radius: float = 0.0 # For CIRCLE
    width: float = 0.0 # For BOX
    height: float = 0.0 # For BOX
    is_trigger: bool = False # If True, detects overlap but no physical response

@register_component()
class SpriteComponent(BaseComponent):
    """Texture for internal rendering"""
    texture_path: str = ""
    scale: float = 1.0
    visible: bool = True

@register_component()
class RewardComponent(BaseComponent):
    """Reward signal for Reinforcement Learning (Gymnasium)"""
    current_reward: float = 0.0
    cumulative_reward: float = 0.0
    is_terminal: bool = False # Episode end flag
