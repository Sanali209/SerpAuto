import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow, GUIEventBus
from serpentine.systems.gui.selection import SelectionService
from serpentine.systems.auto_ui_builder import AutoUIBuilder
from serpentine.core.world import World

class Inspector(BaseUIWindow):
    def __init__(self):
        super().__init__("inspector", "Inspector", width=300, height=400)
        self.current_selected_id = None
        self.current_selected_type = None

    def render(self):
        with dpg.child_window(tag="inspector_content", border=False, autosize_x=True, autosize_y=True):
            dpg.add_text("Nothing selected.")

    def update(self, world: World, dt: float):
        selected = SelectionService.get_selected()
        selected_type = SelectionService.get_selected_type()

        # If selection changed, rebuild UI
        # Or if no selection but UI shows something, clear it.
        if selected != self.current_selected_id or selected_type != self.current_selected_type:
            self.current_selected_id = selected
            self.current_selected_type = selected_type
            self.rebuild_ui(world, selected, selected_type)

        # Poll values? For now no.

    def rebuild_ui(self, world: World, selected, selected_type):
        # Clear previous content
        # Note: dpg.delete_item(item, children_only=True) is not supported in DPG 1.x
        children = dpg.get_item_children("inspector_content", 1)
        if children:
             for child in children:
                 dpg.delete_item(child)

        if selected is None:
            dpg.add_text("Nothing selected.", parent="inspector_content")
            return

        if selected_type == "ENTITY":
            dpg.add_text(f"Entity: {selected}", parent="inspector_content")
            dpg.add_separator(parent="inspector_content")

            # Find components
            components = []
            # Accessing protected member _components as this is a debug tool
            if hasattr(world, '_components'):
                 for comp_type, store in world._components.items():
                    if selected in store:
                        components.append(store[selected])

            if not components:
                dpg.add_text("No components.", parent="inspector_content")
            else:
                for comp in components:
                    comp_name = type(comp).__name__
                    # Use unique tag for header to avoid conflicts? Not really needed if parent is distinct.
                    with dpg.collapsing_header(label=comp_name, default_open=True, parent="inspector_content") as header_tag:
                        # Build UI inside the header
                        AutoUIBuilder.build_ui_for_model(comp, header_tag, f"insp_{selected}_{comp_name}")

        elif selected_type == "NODE":
            dpg.add_text(f"Node: {selected}", parent="inspector_content")
            # Assuming selected is the node instance itself or we can retrieve it
            if hasattr(selected, 'model_dump') or hasattr(selected, '__fields__') or hasattr(selected, 'model_fields'):
                 AutoUIBuilder.build_ui_for_model(selected, "inspector_content", f"insp_node_{id(selected)}")
            else:
                 dpg.add_text(f"Cannot inspect node type: {type(selected)}", parent="inspector_content")

        else:
            dpg.add_text(f"Unknown selection type: {selected_type}", parent="inspector_content")
