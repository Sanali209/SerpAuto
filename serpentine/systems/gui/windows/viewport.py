import dearpygui.dearpygui as dpg
import array
from typing import Optional
try:
    import numpy as np
except ImportError:
    np = None

from serpentine.systems.gui.base import BaseUIWindow
from serpentine.core.world import World
from serpentine.core.event_bus import GUIEventBus
from serpentine.core.registry_v2 import RegistryV2

@RegistryV2.register_window(category="View", icon="👁️", description="Rendered view of the simulation.")
class Viewport(BaseUIWindow):
    def __init__(self):
        super().__init__("viewport_window", "Perception Viewport", width=640, height=480)
        self.texture_tag = "viewport_texture"
        self.texture_registry_tag = "viewport_texture_registry"
        self.texture_width = 640
        self.texture_height = 480
        self.last_pixels_data = None

        GUIEventBus.subscribe("RENDER_COMPLETE", self.on_render_complete)

    def on_render_complete(self, data):
        self.last_pixels_data = data

    def setup(self):
        # Create texture registry if not exists
        if not dpg.does_item_exist(self.texture_registry_tag):
            with dpg.texture_registry(tag=self.texture_registry_tag, show=False):
                # Create initial texture (black)
                # 640*480*4 floats
                initial_data = [0.0] * (self.texture_width * self.texture_height * 4)
                dpg.add_dynamic_texture(
                    width=self.texture_width,
                    height=self.texture_height,
                    default_value=initial_data,
                    tag=self.texture_tag
                )

        # Call base setup to create window and call render()
        super().setup()

    def render(self):
        # We render the image item here.
        # Add image
        # We want to capture clicks on the image.
        dpg.add_image(self.texture_tag, width=self.texture_width, height=self.texture_height, tag=f"{self.window_tag}_image")

        # Add click handler
        with dpg.item_handler_registry(tag=f"{self.window_tag}_handler"):
            dpg.add_item_clicked_handler(callback=self.on_click)

        dpg.bind_item_handler_registry(f"{self.window_tag}_image", f"{self.window_tag}_handler")

    def on_click(self, sender, app_data, user_data):
        # app_data contains (button, )?
        # We need mouse position relative to the image.

        mouse_pos = dpg.get_mouse_pos()
        item_pos = dpg.get_item_pos(f"{self.window_tag}_image")

        if item_pos:
            rel_x = mouse_pos[0] - item_pos[0]
            rel_y = mouse_pos[1] - item_pos[1]

            # Publish event
            GUIEventBus.publish("VIEWPORT_CLICK", {
                "x": rel_x,
                "y": rel_y,
                "width": self.texture_width,
                "height": self.texture_height,
                "button": 0 # TODO: Determine button
            })

    def update(self, world: World, dt: float):
        if self.last_pixels_data and np:
            width = self.last_pixels_data['width']
            height = self.last_pixels_data['height']
            pixels = self.last_pixels_data['pixels'] # bytes
            self.last_pixels_data = None

            if width != self.texture_width or height != self.texture_height:
                # Resize texture logic (complex in DPG, need to delete and recreate?)
                # For now assume fixed size or log warning
                pass

            # Convert bytes to float array
            # pixels is bytes
            # DPG expects list of floats

            # Faster conversion:
            # Assume 0-255 -> 0.0-1.0

            arr = np.frombuffer(pixels, dtype=np.uint8)
            arr = arr.astype(np.float32) / 255.0

            # DPG set_value expects list or flat array?
            # documentation says buffer.
            # It seems numpy array works if flattened?

            dpg.set_value(self.texture_tag, arr)
