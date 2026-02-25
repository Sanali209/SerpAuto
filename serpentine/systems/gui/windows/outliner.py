import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow, GUIEventBus
from serpentine.systems.gui.selection import SelectionService
from serpentine.core.world import World

class Outliner(BaseUIWindow):
    def __init__(self):
        super().__init__("outliner", "World Outliner", width=300, height=400)
        self.filter_text = ""
        self.container_tag = "outliner_list_container"

    def setup(self):
        super().setup()
        # Create container if not exists
        if not dpg.does_item_exist(self.container_tag):
             pass # It's created in render() but setup() calls render() inside window context.

    def render(self):
        with dpg.group(horizontal=True):
            dpg.add_input_text(label="Filter", callback=self.on_filter_change, width=-1)
        dpg.add_separator()

        # Container for the list
        with dpg.child_window(tag=self.container_tag, border=False, autosize_x=True, autosize_y=True):
            pass

    def update(self, world: World, dt: float):
        # Clear previous list
        # dpg.delete_item(self.container_tag, children_only=True) # Not supported

        children = dpg.get_item_children(self.container_tag, 1)
        if children:
            for child in children:
                dpg.delete_item(child)

        # Get selected entity
        selected = SelectionService.get_selected()
        selected_type = SelectionService.get_selected_type()

        # Iterate entities
        # Accessing protected member _entities as this is a debug tool
        # We need to access the set directly
        try:
             entities = sorted(list(world._entities), key=lambda x: str(x))
        except AttributeError:
             # Fallback if _entities is not accessible or renamed
             entities = []

        for entity_id in entities:
            entity_str = str(entity_id)
            if self.filter_text and self.filter_text.lower() not in entity_str.lower():
                continue

            is_selected = (selected == entity_id and selected_type == "ENTITY")

            # Use selectable
            dpg.add_selectable(label=entity_str, default_value=is_selected,
                               parent=self.container_tag,
                               callback=self.on_select, user_data=entity_id)

    def on_filter_change(self, sender, app_data):
        self.filter_text = app_data

    def on_select(self, sender, app_data, user_data):
        # Select the entity
        SelectionService.set_selected(user_data, "ENTITY")
