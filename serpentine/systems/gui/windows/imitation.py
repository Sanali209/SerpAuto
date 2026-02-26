import dearpygui.dearpygui as dpg
import time
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.core.registry_v2 import RegistryV2
from serpentine.core.world import World
from serpentine.core.selection import SelectionService
from serpentine.perception.components import ActionBufferComponent
from serpentine.mind.intent import Intent

@RegistryV2.register_window(category="Analytics", icon="👥", description="Compare Human vs AI.")
class ImitationLearningMonitor(BaseUIWindow):
    def __init__(self):
        super().__init__("imitation_monitor", "Imitation Learning Monitor", width=600, height=400)
        self.plot_tag = "imitation_loss_plot"
        self.series_tag = "imitation_loss_series"
        self.loss_history = []
        self.max_points = 100

    def render(self):
        with dpg.plot(label="Imitation Loss", height=-1, width=-1, tag=self.plot_tag):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Time")
            with dpg.plot_axis(dpg.mvYAxis, label="Loss", tag="y_axis"):
                dpg.add_line_series([], [], label="Loss", tag=self.series_tag)
                dpg.set_axis_limits("y_axis", 0, 1.1)

    def update(self, world: World, dt: float):
        selected = SelectionService.get_selected()
        if not selected:
            return

        buffer = world.get_component(selected, ActionBufferComponent)
        if not buffer:
            return

        # Compare
        # Check recent history for human action
        now = time.time()
        # Allow a small buffer for timing differences
        window = max(dt, 0.05)

        human_action = None
        if buffer.history:
            last_time, last_action = buffer.history[-1]
            if now - last_time < window:
                human_action = last_action

        ai_action = buffer.shadow_queue[0] if buffer.shadow_queue else None

        loss = 0.0

        # Case 1: Both None (Correct inaction)
        if human_action is None and ai_action is None:
            loss = 0.0

        # Case 2: One is None (Missed action or Hallucination)
        elif (human_action is None) != (ai_action is None):
            loss = 1.0

        # Case 3: Both acted
        else:
            if human_action.type != ai_action.type:
                loss = 1.0
            else:
                # Compare params
                # Simple check: string representation match?
                # Or specific fields.
                # For now, simplistic.
                # We can check important fields based on type
                if human_action.type == "move":
                    # Allow some tolerance for coordinates
                    dist = ((human_action.x - ai_action.x)**2 + (human_action.y - ai_action.y)**2)**0.5
                    if dist > 10: # 10 pixels tolerance
                        loss = 0.5
                elif str(human_action) != str(ai_action):
                    loss = 0.5 # Partial match

        # Clear shadow queue to keep sync
        # Because next tick AI will predict again based on new state.
        buffer.shadow_queue.clear()

        self.loss_history.append(loss)
        if len(self.loss_history) > self.max_points:
            self.loss_history.pop(0)

        # Update plot
        # DPG expects distinct lists for X and Y
        if dpg.does_item_exist(self.series_tag):
            dpg.set_value(self.series_tag, [list(range(len(self.loss_history))), self.loss_history])
