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
            
            # Skip if waiting for external I/O (e.g. LLM call)
            if brain.status == "WAITING_FOR_IO":
                continue

            if brain.bt_root:
                # Tick the Behavior Tree
                status = await brain.bt_root.tick(world, entity)
                brain.status = status.value
