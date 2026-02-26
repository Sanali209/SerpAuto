import dearpygui.dearpygui as dpg
from typing import Optional, Dict, Any, Tuple
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.systems.gui.graph.base import BaseNodeCanvas
from serpentine.core.registry_v2 import RegistryV2
from serpentine.core.selection import SelectionService
from serpentine.mind.brain import BrainComponent
from serpentine.mind.core import BehaviorTreeNode, Status
from serpentine.mind.composites import Sequence, Selector, Parallel
from serpentine.mind.decorators import Inverter, Succeeder, RepeatUntilFail

@RegistryV2.register_window(category="Tools", icon="🌳", description="Visual editor for Behavior Trees.")
class BehaviorTreeEditor(BaseUIWindow):
    def __init__(self):
        super().__init__(window_tag="bt_editor", label="Behavior Tree Editor", width=1200, height=800)
        self.canvas = BaseNodeCanvas(tag="bt_editor_canvas")
        self.last_entity_id = None
        self.node_positions: Dict[int, Tuple[int, int]] = {}
        self.layout_calculated = False

    def render(self):
        with dpg.group(horizontal=True):
            # Left Sidebar
            with dpg.child_window(width=200, height=-1):
                dpg.add_text("Nodes")
                dpg.add_separator()

                categories = ["Composites", "Decorators", "Actions", "Conditions"]
                for category in categories:
                    if dpg.collapsing_header(label=category, default_open=True):
                        nodes = RegistryV2.get_nodes_by_category(category)
                        for node_cls in nodes:
                            meta = RegistryV2.get_node_metadata(node_cls.__name__)
                            label = f"{meta.icon} {node_cls.__name__}" if meta else node_cls.__name__
                            dpg.add_button(label=label, width=-1)
                            # Drag and drop source could be added here

            # Main Canvas
            with dpg.child_window(border=False):
                self.canvas.render()

    def update(self, world: Any, dt: float):
        selected_entity = SelectionService.get_selected()
        selected_type = SelectionService.get_selected_type()

        # Only update if we have an entity selection
        if not selected_entity or selected_type != "ENTITY":
            # Potentially clear canvas or show "No Selection"
            # self.canvas.clear()
            return

        # Check if entity has BrainComponent
        # SelectionService returns ID or Object? Usually ID for entities.
        # Assuming ID.
        brain = world.get_component(selected_entity, BrainComponent)
        if not brain or not brain.root:
            return

        # If selection changed, recalculate layout
        if selected_entity != self.last_entity_id:
            self.canvas.clear()
            self.node_positions.clear()
            self.layout_calculated = False
            self.last_entity_id = selected_entity

        # Calculate layout once
        if not self.layout_calculated:
            self._calculate_layout(brain.root, 100, 100)
            self.layout_calculated = True

        # Render Tree
        self._render_tree(brain.root)

    def _calculate_layout(self, node: BehaviorTreeNode, x: int, y: int) -> int:
        """
        Calculates positions for nodes recursively.
        Returns the maximum Y used by this subtree.
        """
        self.node_positions[id(node)] = (x, y)

        children = self._get_children(node)
        if not children:
            return y + 100

        current_y = y
        child_x = x + 250 # Horizontal spacing

        for child in children:
            max_child_y = self._calculate_layout(child, child_x, current_y)
            current_y = max_child_y

        return current_y

    def _get_children(self, node: BehaviorTreeNode) -> list:
        if hasattr(node, "children"):
            return node.children
        elif hasattr(node, "child"):
            return [node.child]
        return []

    def _render_tree(self, node: BehaviorTreeNode):
        node_id = id(node)
        pos = self.node_positions.get(node_id, (0, 0))

        # Determine Color based on Status
        color = (100, 100, 100) # Default Gray
        if node.status == Status.SUCCESS:
            color = (50, 200, 50) # Green
        elif node.status == Status.FAILURE:
            color = (200, 50, 50) # Red
        elif node.status == Status.RUNNING:
            color = (50, 50, 200) # Blue

        # Tag generation
        node_tag = f"bt_node_{node_id}"
        input_tag = f"bt_in_{node_id}"
        output_tag = f"bt_out_{node_id}"

        # Setup Attributes
        inputs = [(input_tag, "In")]
        outputs = []

        children = self._get_children(node)
        if children:
             outputs = [(output_tag, "Out")]

        # Add Node
        # We pass node type name as label
        label = type(node).__name__
        self.canvas.add_node(node_tag, label, pos, inputs=inputs, outputs=outputs, color=color)

        # Add Links
        if children:
            for child in children:
                child_id = id(child)
                child_in_tag = f"bt_in_{child_id}"
                link_tag = f"link_{node_id}_{child_id}"

                self.canvas.add_link(link_tag, output_tag, child_in_tag)

                # Recurse
                self._render_tree(child)
