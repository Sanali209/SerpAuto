import dearpygui.dearpygui as dpg
from typing import List, Optional, Tuple, Any

class BaseNodeCanvas:
    """
    A reusable wrapper around DearPyGui's Node Editor.
    Handles basic node and link management.
    """
    def __init__(self, tag: str):
        self.tag = tag
        self.nodes = set()
        self.links = set()
        self.theme_cache = {}  # Cache themes by color tuple

    def render(self):
        """Creates the node editor widget."""
        # Note: If this is called every frame, it will error. It should be called once in setup/render of the window.
        if not dpg.does_item_exist(self.tag):
            with dpg.node_editor(tag=self.tag, callback=self._on_link, delink_callback=self._on_del_link):
                pass

    def clear(self):
        """Clears all nodes and links from the canvas."""
        # Using delete_item on children of the editor
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag, children_only=True)
        self.nodes.clear()
        self.links.clear()

    def add_node(self, node_tag: str, label: str, pos: Tuple[int, int],
                 inputs: List[Tuple[str, str]] = [],
                 outputs: List[Tuple[str, str]] = [],
                 color: Optional[Tuple[float, float, float]] = None):
        """
        Adds or updates a node on the canvas.
        Args:
            node_tag: Unique tag for the node.
            label: Display label.
            pos: (x, y) position.
            inputs: List of (attr_tag, label) for input pins.
            outputs: List of (attr_tag, label) for output pins.
            color: Optional (R, G, B) color (0-255) for the node header.
        """
        if dpg.does_item_exist(node_tag):
            # Update position
            # We don't update attributes dynamically for now to avoid complexity
            current_pos = dpg.get_item_pos(node_tag)
            # Only update if significantly different to avoid jitter?
            # DPG handles this efficiently usually.
            # But if user drags, we don't want to snap back unless logic dictates.
            # For visualization, we might want to force position or let user drag.
            # If we are strictly visualizing logic, we might force it.
            # Let's assume layout is handled by caller.
            dpg.set_item_pos(node_tag, pos)

            # Update color if changed
            # Theme binding is expensive to redo every frame?
            # We can check if status changed.
            # Let's just bind it.
            if color:
                theme_tag = self._get_or_create_theme(color)
                dpg.bind_item_theme(node_tag, theme_tag)
            return

        with dpg.node(tag=node_tag, parent=self.tag, label=label, pos=pos):
            # Input attributes
            for attr_tag, attr_label in inputs:
                with dpg.node_attribute(tag=attr_tag, attribute_type=dpg.mvNode_Attribute_Input):
                    dpg.add_text(attr_label)

            # Output attributes
            for attr_tag, attr_label in outputs:
                with dpg.node_attribute(tag=attr_tag, attribute_type=dpg.mvNode_Attribute_Output):
                    dpg.add_text(attr_label)

        if color:
            theme_tag = self._get_or_create_theme(color)
            dpg.bind_item_theme(node_tag, theme_tag)

        self.nodes.add(node_tag)

    def _get_or_create_theme(self, color: Tuple[float, float, float]) -> str:
        """Retrieves a cached theme tag for the given color or creates a new one."""
        if color in self.theme_cache:
            return self.theme_cache[color]

        theme_tag = f"theme_{self.tag}_{color}"
        with dpg.theme(tag=theme_tag):
            with dpg.theme_component(dpg.mvNode):
                dpg.add_theme_color(dpg.mvNodeCol_TitleBar, color, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvNodeCol_TitleBarHovered, color, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvNodeCol_TitleBarSelected, color, category=dpg.mvThemeCat_Core)

        self.theme_cache[color] = theme_tag
        return theme_tag

    def add_link(self, link_tag: str, attr1: str, attr2: str):
        """
        Adds a link between two attributes (pins).
        Args:
            link_tag: Unique tag for the link.
            attr1: Source attribute tag (Output).
            attr2: Target attribute tag (Input).
        """
        if dpg.does_item_exist(link_tag):
            return

        if not dpg.does_item_exist(attr1) or not dpg.does_item_exist(attr2):
            return

        dpg.add_node_link(tag=link_tag, parent=self.tag, attribute1=attr1, attribute2=attr2)
        self.links.add(link_tag)

    def _on_link(self, sender, app_data):
        # app_data is (link_id, attr1, attr2)
        # Handle manual linking
        pass

    def _on_del_link(self, sender, app_data):
        # app_data is link_id
        if dpg.does_item_exist(app_data):
            dpg.delete_item(app_data)
        if app_data in self.links:
            self.links.remove(app_data)
