import dearpygui.dearpygui as dpg
import time
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.core.registry_v2 import RegistryV2
from serpentine.core.world import World
from serpentine.core.selection import SelectionService
from serpentine.perception.components import ActionBufferComponent

@RegistryV2.register_window(category="Analytics", icon="⏱️", description="Action execution history.")
class ActionTimelineWindow(BaseUIWindow):
    def __init__(self):
        super().__init__("action_timeline", "Action Timeline", width=600, height=200)
        self.draw_node = "timeline_draw_node"

    def render(self):
        with dpg.drawlist(width=580, height=160, tag=self.draw_node):
            pass

    def update(self, world: World, dt: float):
        if dpg.does_item_exist(self.draw_node):
            dpg.delete_item(self.draw_node, children_only=True)

        selected = SelectionService.get_selected()
        selected_type = SelectionService.get_selected_type()

        if not selected or selected_type != "ENTITY":
            dpg.draw_text((10, 10), "No entity selected", parent=self.draw_node, size=16)
            return

        buffer = world.get_component(selected, ActionBufferComponent)
        if not buffer:
            dpg.draw_text((10, 10), "Selected entity has no ActionBuffer", parent=self.draw_node, size=16)
            return

        # Draw timeline
        # X axis: Time.
        # We want to show last 10 seconds.
        now = time.time()
        window_size = 10.0 # seconds
        width = 580
        height = 160
        pixels_per_sec = width / window_size

        # Draw background lines
        for i in range(11):
            x = width - (i * pixels_per_sec)
            dpg.draw_line((x, 0), (x, height), color=(50, 50, 50), parent=self.draw_node)

        # Draw actions
        # history is List[Tuple[float, Intent]]
        for timestamp, action in buffer.history:
            age = now - timestamp
            if age > window_size:
                continue

            x = width - (age * pixels_per_sec)
            y = 50

            # Determine color and duration
            color = (200, 200, 200)
            duration = 0.1 # default visual width in seconds

            if action.type == "move":
                color = (100, 100, 255) # Blue
                duration = getattr(action, 'duration', 0.1) or 0.1
            elif action.type == "click":
                color = (255, 100, 100) # Red
            elif action.type == "key":
                color = (100, 255, 100) # Green
            elif action.type == "change_direction":
                color = (255, 255, 100) # Yellow

            w = max(5, duration * pixels_per_sec)

            # Draw block
            # x is right edge (start time + duration?) No, timestamp is start time.
            # So x corresponds to timestamp.
            # Wait, timeline usually flows left. Oldest on left.
            # age = 0 (now) -> x = width
            # age = 10 -> x = 0

            # If timestamp is T, and now is N.
            # x = width - (N - T) * pps

            rect_start = (x, y)
            rect_end = (x + w, y + 20)

            dpg.draw_rectangle(rect_start, rect_end, color=color, fill=color, parent=self.draw_node)
            dpg.draw_text((x, y - 15), action.type, size=12, parent=self.draw_node)
