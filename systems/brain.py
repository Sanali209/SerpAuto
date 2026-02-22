from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import BrainComponent

@register_system(phase=Phase.COGNITION)
class AI_BrainSystem(System):
    """
    Executes the Behavior Tree for each agent.
    """
    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(BrainComponent)
        for entity in entities:
            brain = world.get_component(entity, BrainComponent)

            # Here we would fetch the root node of the BT for this agent
            # status = await root_node.tick(world, entity)

            # Update status
            # brain.status = status.value
            pass
