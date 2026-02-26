import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow, GUIEventBus
from serpentine.core.selection import SelectionService
from serpentine.systems.auto_ui_builder import AutoUIBuilder
from serpentine.core.registry_v2 import RegistryV2
from serpentine.core.world import World

@RegistryV2.register_window(category="Tools", icon="🔍", description="Inspect and edit properties of selected objects.")
class Inspector(BaseUIWindow):
    def __init__(self):
        super().__init__("inspector", "Inspector", width=300, height=400)
        self.current_selected_id = None
        self.current_selected_type = None
        self.container_tag = "inspector_content"
        self.needs_rebuild = False

    def setup(self):
        super().setup()
        GUIEventBus.subscribe("ON_SELECTION_CHANGED", self.on_selection_changed)

    def render(self):
        with dpg.child_window(tag=self.container_tag, border=False, autosize_x=True, autosize_y=True):
            dpg.add_text("Nothing selected.")

    def on_selection_changed(self, data):
        self.needs_rebuild = True

    def update(self, world: World, dt: float):
        if self.needs_rebuild:
            self.needs_rebuild = False
            selected = SelectionService.get_selected()
            selected_type = SelectionService.get_selected_type()

            self.current_selected_id = selected
            self.current_selected_type = selected_type

            self.rebuild_ui(world, selected, selected_type)

    def rebuild_ui(self, world: World, selected, selected_type):
        dpg.delete_item(self.container_tag, children_only=True)

        if selected is None:
            dpg.add_text("Nothing selected.", parent=self.container_tag)
            return

        if selected_type == "ENTITY":
            dpg.add_text(f"Entity: {selected}", parent=self.container_tag)
            dpg.add_separator(parent=self.container_tag)

            # Find components
            components = []
            if hasattr(world, '_components'):
                 for comp_type, store in world._components.items():
                    if selected in store:
                        components.append(store[selected])

            if not components:
                dpg.add_text("No components.", parent=self.container_tag)
            else:
                for comp in components:
                    comp_name = type(comp).__name__
                    with dpg.collapsing_header(label=comp_name, default_open=True, parent=self.container_tag) as header_tag:
                        AutoUIBuilder.build_ui_for_model(comp, header_tag, f"insp_{selected}_{comp_name}")

        elif selected_type == "NODE":
            dpg.add_text(f"Node: {selected}", parent=self.container_tag)
            # Assuming selected is the node instance itself
            if hasattr(selected, 'model_dump') or hasattr(selected, '__fields__') or hasattr(selected, 'model_fields'):
                 AutoUIBuilder.build_ui_for_model(selected, self.container_tag, f"insp_node_{id(selected)}")
            else:
                 dpg.add_text(f"Cannot inspect node type: {type(selected)}", parent=self.container_tag)

        else:
            dpg.add_text(f"Unknown selection type: {selected_type}", parent=self.container_tag)
