import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.core.event_bus import GUIEventBus
from serpentine.core.world import World
from serpentine.components.simulation import DatasetConfigComponent

class ControlDeck(BaseUIWindow):
    def __init__(self):
        super().__init__("control_deck", "Control Deck", width=300, height=150)
        self.paused = False
        self.tps = 60
        self.rec_requested = False

    def render(self):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Play", callback=self.on_play)
            dpg.add_button(label="Pause", callback=self.on_pause)
            dpg.add_button(label="Step", callback=self.on_step)
            dpg.add_button(label="REC", callback=self.on_rec_toggle)
            dpg.add_button(label="Save", callback=self.on_save_click)
            dpg.add_button(label="Load", callback=self.on_load_click)

        dpg.add_separator()
        dpg.add_drag_int(label="TPS", default_value=self.tps, min_value=1, max_value=240, callback=self.on_tps_change)

        dpg.add_separator()
        self.fps_text = dpg.add_text("FPS: 0")

    def update(self, world: World, dt: float):
        if dt > 0:
            fps = int(1.0 / dt)
            dpg.set_value(self.fps_text, f"FPS: {fps}")

        if self.rec_requested:
            entities = world.get_entities_with(DatasetConfigComponent)
            for _, config in entities:
                config.is_recording = not config.is_recording
                # Optionally log state change
                print(f"Recording {'started' if config.is_recording else 'stopped'}")
            self.rec_requested = False

    def on_rec_toggle(self, sender, app_data):
        self.rec_requested = True

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

    def on_save_click(self):
        dpg.add_file_dialog(
            label="Save Snapshot",
            width=600,
            height=400,
            callback=self.on_save_selected,
            default_filename="snapshot.json"
        )

    def on_load_click(self):
        dpg.add_file_dialog(
            label="Load Snapshot",
            width=600,
            height=400,
            callback=self.on_load_selected
        )

    def on_save_selected(self, sender, app_data):
        filepath = app_data.get('file_path_name')
        if filepath:
            GUIEventBus.publish("ENGINE_SAVE_SNAPSHOT", filepath)

    def on_load_selected(self, sender, app_data):
        filepath = app_data.get('file_path_name')
        if filepath:
            GUIEventBus.publish("ENGINE_LOAD_SNAPSHOT", filepath)
