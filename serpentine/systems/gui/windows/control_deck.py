import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow, GUIEventBus
from serpentine.core.world import World

class ControlDeck(BaseUIWindow):
    def __init__(self):
        super().__init__("control_deck", "Control Deck", width=300, height=150)
        self.paused = False
        self.tps = 60

    def render(self):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Play", callback=self.on_play)
            dpg.add_button(label="Pause", callback=self.on_pause)
            dpg.add_button(label="Step", callback=self.on_step)

        dpg.add_separator()
        dpg.add_drag_int(label="TPS", default_value=self.tps, min_value=1, max_value=240, callback=self.on_tps_change)

        dpg.add_separator()
        self.fps_text = dpg.add_text("FPS: 0")

    def update(self, world: World, dt: float):
        if dt > 0:
            fps = int(1.0 / dt)
            dpg.set_value(self.fps_text, f"FPS: {fps}")

    def on_play(self):
        self.paused = False
        GUIEventBus.publish("ENGINE_PLAY")

    def on_pause(self):
        self.paused = True
        GUIEventBus.publish("ENGINE_PAUSE")

    def on_step(self):
        GUIEventBus.publish("ENGINE_STEP")

    def on_tps_change(self, sender, app_data):
        self.tps = app_data
        GUIEventBus.publish("ENGINE_SET_TPS", self.tps)
