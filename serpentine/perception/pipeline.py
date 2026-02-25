from typing import List, Dict, Any
from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.perception.components import PerceptionComponent
from serpentine.perception.nodes import PerceptionNode, CropNode, GrayscaleNode, OCRNode

@Registry.register_system(phase=SystemPhase.PERCEPTION, modes=[EngineMode.ARCHITECT, EngineMode.TEACHER, EngineMode.PRODUCTION])
class PerceptionPipelineSystem(System):
    """
    Executes the perception pipeline.
    Currently implements a linear sequence of nodes for demonstration.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)

        # TODO: Load pipeline configuration from file/blueprint
        self.nodes: List[PerceptionNode] = [
            CropNode(name="center_crop"),
            GrayscaleNode(name="grayscale_view")
        ]

    async def update(self, world: World, dt: float) -> None:
        entities = world.get_components(PerceptionComponent)

        for entity_id, perception in entities.items():
            # Start with raw screen input
            current_obs = perception.get_observation("raw_screen")
            if not current_obs:
                continue

            # Run the pipeline
            for node in self.nodes:
                result = None

                # Logic to pass specific params to nodes would go here or be part of the node config
                if node.name == "center_crop":
                    # Example: crop center
                    # We need image dimensions.
                    # Assuming metadata has width/height or we check the image
                    w = current_obs.metadata.get("width", 1920)
                    h = current_obs.metadata.get("height", 1080)

                    # Safe default if metadata missing
                    if w == 0 or h == 0:
                        continue

                    cx, cy = w // 2, h // 2
                    # Crop 400x400 center
                    roi = (cx - 200, cy - 200, 400, 400)
                    result = node.process(current_obs, roi=roi)

                else:
                    # Generic process
                    result = node.process(current_obs)

                if result:
                    # Store intermediate results
                    perception.add_observation(node.name, result)
                    # Pass output to next node
                    current_obs = result
                else:
                    # If a node fails or returns None, we might stop this branch
                    # For a linear pipeline, we break
                    break
