import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.core.world import World

class Viewport(BaseUIWindow):
    def __init__(self):
        super().__init__("viewport", "Perception Viewport", width=640, height=480)
        self.texture_tag = "viewport_texture"
        self.texture_width = 640
        self.texture_height = 480
        self.texture_registered = False

    def render(self):
        dpg.add_text("Perception Viewport (Placeholder)")
        # In future: dpg.add_image(self.texture_tag)

    def update(self, world: World, dt: float):
        # Update texture from PerceptionComponent
        pass
