import dearpygui.dearpygui as dpg
from typing import Any
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.systems.gui.graph.base import BaseNodeCanvas
from serpentine.perception.pipeline import PerceptionPipelineSystem
from serpentine.core.registry_v2 import RegistryV2

@RegistryV2.register_window(category="Tools", icon="👁️", description="Visual editor for Perception Pipelines.")
class PerceptionGraphEditor(BaseUIWindow):
    def __init__(self):
        super().__init__(window_tag="perception_editor", label="Perception Pipeline Editor", width=1200, height=600)
        self.canvas = BaseNodeCanvas(tag="perception_editor_canvas")
        # Instantiate a dummy system to inspect the default configuration
        # NOTE: This creates a disconnected instance and does not reflect runtime changes.
        # Ideally, we should retrieve the active PerceptionPipelineSystem from the engine,
        # but the current architecture doesn't expose systems via the World.
        # Since the pipeline configuration is currently hardcoded and static, this is acceptable for visualization.
        self.pipeline_system = PerceptionPipelineSystem(tick_rate=None)
        self.nodes_initialized = False

    def render(self):
        with dpg.child_window(border=False):
            self.canvas.render()

    def update(self, world: Any, dt: float):
        if not self.nodes_initialized:
            self._initialize_graph()
            self.nodes_initialized = True

        # Here we could update node colors based on execution time or status if available
        pass

    def _initialize_graph(self):
        x = 50
        y = 250
        spacing = 300

        # Start Node (Raw Input)
        start_id = "perception_start"
        self.canvas.add_node(
            node_tag=start_id,
            label="Input: Screen",
            pos=(x, y),
            inputs=[],
            outputs=[(f"{start_id}_out", "Raw Image")],
            color=(50, 50, 150)
        )
        x += spacing

        previous_out_tag = f"{start_id}_out"

        for i, node in enumerate(self.pipeline_system.nodes):
            node_tag = f"perception_node_{i}"
            in_tag = f"{node_tag}_in"
            out_tag = f"{node_tag}_out"

            # Use node name or class name
            label = getattr(node, "name", type(node).__name__)

            self.canvas.add_node(
                node_tag=node_tag,
                label=label,
                pos=(x, y),
                inputs=[(in_tag, "In")],
                outputs=[(out_tag, "Out")],
                color=(50, 100, 50)
            )

            # Link to previous
            link_tag = f"link_perc_{i}"
            self.canvas.add_link(link_tag, previous_out_tag, in_tag)

            previous_out_tag = out_tag
            x += spacing

        # End Node (Actions/Output)
        end_id = "perception_end"
        self.canvas.add_node(
            node_tag=end_id,
            label="Output",
            pos=(x, y),
            inputs=[(f"{end_id}_in", "Features")],
            outputs=[],
            color=(150, 50, 50)
        )

        self.canvas.add_link("link_perc_end", previous_out_tag, f"{end_id}_in")
