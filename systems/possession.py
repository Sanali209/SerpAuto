from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import PlayerControllerComponent, CameraComponent, BrainComponent

@register_system(phase=Phase.EXECUTION)
class PossessionSystem(System):
    """
    Handles swapping control between AI and Player.
    Logic:
    1. Remove PlayerControllerComponent from current entity.
    2. Add BrainComponent to it.
    3. Remove BrainComponent from target.
    4. Add PlayerControllerComponent to target.
    5. Re-bind CameraComponent.
    """
    def __init__(self, toggle_key: int = None):
        self.toggle_key = toggle_key

    async def update(self, world: World, dt: float):
        # Implementation of possession logic triggered by events or specific conditions
        # For now, this serves as a manager for player-owned entities.
        pass

    def possess(self, world: World, from_entity: str, to_entity: str):
        # Logic to swap components
        if world.has_component(from_entity, PlayerControllerComponent):
            world.remove_component(from_entity, PlayerControllerComponent)
            if not world.has_component(from_entity, BrainComponent):
                world.add_component(from_entity, BrainComponent())
        
        if world.has_component(to_entity, BrainComponent):
            world.remove_component(to_entity, BrainComponent)
            if not world.has_component(to_entity, PlayerControllerComponent):
                world.add_component(to_entity, PlayerControllerComponent())
        
        # Move camera if exists
        if world.has_component(from_entity, CameraComponent):
            cam = world.remove_component(from_entity, CameraComponent)
            world.add_component(to_entity, cam)
