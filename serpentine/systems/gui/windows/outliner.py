import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.core.selection import SelectionService
from serpentine.core.registry_v2 import RegistryV2
from serpentine.core.world import World

@RegistryV2.register_window(category="Tools", icon="📝", description="View and select entities in the world.")
class Outliner(BaseUIWindow):
    def __init__(self):
        super().__init__("outliner", "World Outliner", width=300, height=400)
        self.filter_text = ""
        self.container_tag = "outliner_list_container"

    def render(self):
        with dpg.group(horizontal=True):
            dpg.add_input_text(label="Filter", callback=self.on_filter_change, width=-1)
        dpg.add_separator()

        # Container for the list
        with dpg.child_window(tag=self.container_tag, border=False, autosize_x=True, autosize_y=True):
            pass

    def update(self, world: World, dt: float):
        # Clear previous list
        # Note: If children_only=True works, use it. If not, fallback.
        # Using delete_item on children is slow.
        # But for now we follow the pattern.
        dpg.delete_item(self.container_tag, children_only=True)

        # Get selected entity
        selected = SelectionService.get_selected()
        selected_type = SelectionService.get_selected_type()

        # Iterate entities
        try:
             # Sort entities for consistent order
             entities = sorted(list(world._entities), key=lambda x: str(x))
        except AttributeError:
             entities = []

        for entity_id in entities:
            entity_str = str(entity_id)
            if self.filter_text and self.filter_text.lower() not in entity_str.lower():
                continue

            is_selected = (selected == entity_id and selected_type == "ENTITY")

            dpg.add_selectable(label=entity_str, default_value=is_selected,
                               parent=self.container_tag,
                               callback=self.on_select, user_data=entity_id)

    def on_filter_change(self, sender, app_data):
        self.filter_text = app_data

    def on_select(self, sender, app_data, user_data):
        if app_data:
            SelectionService.set_selected(user_data, "ENTITY")
        else:
            if SelectionService.get_selected() == user_data:
                SelectionService.clear_selection()
