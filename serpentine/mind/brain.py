from typing import Optional, Any
try:
    from pydantic import BaseModel, Field
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, Field

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.core.component import BaseComponent
from serpentine.systems.base import System
from serpentine.mind.core import BehaviorTreeNode, Blackboard, Status

@Registry.register_component
class BrainComponent(BaseComponent):
    """
    Holds the cognitive state of an entity.
    """
    root: Optional[BehaviorTreeNode] = None
    blackboard: Blackboard = Field(default_factory=Blackboard)
    active: bool = True

@Registry.register_system(phase=SystemPhase.COGNITION, modes=[EngineMode.PRODUCTION, EngineMode.TEACHER, EngineMode.GYMNASIUM, EngineMode.CONTINUOUS_LEARNING])
class AI_BrainSystem(System):
    """
    Executes Behavior Trees for all entities with a BrainComponent.
    """
    async def update(self, world: Any, dt: float) -> None:
        # get_components returns Dict[UUID, Component]
        entities = world.get_components(BrainComponent)

        for entity_id, brain in entities.items():
            if not brain.active or not brain.root:
                continue

            # Execute the BT
            await brain.root.tick(world, entity_id, brain.blackboard)
