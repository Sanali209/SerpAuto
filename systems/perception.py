from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import PerceptionComponent
from perception.cv_nodes import ScreenCaptureNode

@register_system(phase=Phase.PERCEPTION)
class SensoryInputSystem(System):
    """
    Ingests raw data from the environment (Screenshot, DOM, Internal State).
    """
    def __init__(self):
        self.capturer = ScreenCaptureNode()

    async def update(self, world: World, dt: float):
        from components.core import BrainComponent
        entities = world.get_entities_with(PerceptionComponent)
        
        try:
            raw_frame = self.capturer.process({})
            
            for entity in entities:
                perception = world.get_component(entity, PerceptionComponent)
                if perception:
                    perception.raw_context["_raw_frame"] = raw_frame

                brain = world.get_component(entity, BrainComponent)
                if brain and brain.status == "WAITING_FOR_IO":
                    brain.status = "READY_TO_LEARN"
        except Exception as e:
            print(f"[Sensory] Error: {e}")
