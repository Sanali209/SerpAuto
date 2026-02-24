from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import PerceptionComponent
from perception.cv_nodes import ScreenCaptureNode, CropNode, GrayscaleNode, YOLONode

@register_system(phase=Phase.PERCEPTION)
class PerceptionPipelineSystem(System):
    """
    Processes raw input data (from SensoryInputSystem) through a DAG of filter nodes
    and updates the PerceptionComponent.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        return cls._instance

    def __init__(self, nodes: list = None):
        PerceptionPipelineSystem._instance = self
        # In a real app, these would be configured via scene JSON
        self.nodes = nodes if nodes is not None else [ScreenCaptureNode()]

    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(PerceptionComponent)
        for entity in entities:
            perception = world.get_component(entity, PerceptionComponent)
            
            # Prepare context
            context = perception.raw_context
            # Ensure we have a frame to work with
            frame = context.get("_raw_frame")
            if frame is None:
                continue

            context["_world"] = world
            context["_entity_id"] = entity
            
            # Run Nodes sequentially
            current_frame = frame
            for i, node in enumerate(self.nodes):
                try:
                    if hasattr(node, 'process'):
                        res = node.process(current_frame)
                        if isinstance(res, np.ndarray):
                            current_frame = res
                        elif isinstance(res, dict):
                            context.update(res)
                except Exception as e:
                    print(f"[Pipeline] Node {i} ({node.__class__.__name__}) failed: {e}")
            
            perception.processed_frame = current_frame
            perception.raw_context = context
