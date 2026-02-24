import dearpygui.dearpygui as dpg
from core.registry import Registry

class SystemInspector:
    """
    GUI module for monitoring and managing active engine systems.
    Allows toggling systems and adjusting their update tick rates.
    """
    def __init__(self, window_tag="SystemInspectorWindow"):
        self.window_tag = window_tag
        self._setup_window()

    def _setup_window(self):
        with dpg.window(label="System Inspector", tag=self.window_tag, width=400, height=300, pos=(970, 350)):
            dpg.add_text("Active Systems (Phase Order):")
            dpg.add_separator()
            with dpg.child_window(tag="systems_list_child", height=-1):
                pass

    def update(self, engine):
        """Refreshes the list of systems and their statuses."""
        if not dpg.is_item_visible(self.window_tag):
            return

        dpg.delete_item("systems_list_child", children_only=True)
        
        # In SerpentineEngineV2, systems are stored in self.systems [System]
        for system in engine.systems:
            sys_name = system.__class__.__name__
            phase = getattr(system, 'phase', 'Unknown')
            
            with dpg.group(parent="systems_list_child"):
                with dpg.group(horizontal=True):
                    # Status Indicator
                    is_enabled = getattr(system, 'enabled', True)
                    color = (0, 255, 0) if is_enabled else (150, 150, 150)
                    dpg.add_text("● ", color=color)
                    dpg.add_text(f"{sys_name} ({phase})")
                    
                    # Toggle Button
                    def toggle_cb(sender, app_data, user_data):
                        sys_ref = user_data
                        sys_ref.enabled = not getattr(sys_ref, 'enabled', True)
                    
                    dpg.add_button(label="Toggle", small=True, callback=toggle_cb, user_data=system)
                
                # Metadata (if any)
                if hasattr(system, 'dt_accum'):
                    dpg.add_text(f"  Accumulator: {system.dt_accum:.4f}s", color=(150, 150, 150))
                
                dpg.add_separator()
