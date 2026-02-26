import dearpygui.dearpygui as dpg
from serpentine.systems.gui.base import BaseUIWindow
from serpentine.core.registry_v2 import RegistryV2
from serpentine.core.world import World
from serpentine.core.selection import SelectionService
from serpentine.mind.brain import BrainComponent
from serpentine.components.standard import StatsComponent

@RegistryV2.register_window(category="Analytics", icon="📊", description="Real-time swarm monitoring.")
class GlobalSwarmRoster(BaseUIWindow):
    def __init__(self):
        super().__init__("swarm_roster", "Global Swarm Roster", width=600, height=400)
        self.table_tag = "roster_table"

    def render(self):
        with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp,
                       borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True,
                       tag=self.table_tag, scrollY=True):
            dpg.add_table_column(label="ID", width_stretch=True, init_width_or_weight=2.0)
            dpg.add_table_column(label="BT Status", width_stretch=True, init_width_or_weight=1.0)
            dpg.add_table_column(label="FPS", width_stretch=True, init_width_or_weight=0.5)
            dpg.add_table_column(label="CPU", width_stretch=True, init_width_or_weight=0.5)
            dpg.add_table_column(label="Health", width_stretch=True, init_width_or_weight=0.5)
            dpg.add_table_column(label="Stamina", width_stretch=True, init_width_or_weight=0.5)
            dpg.add_table_column(label="Focus", width_fixed=True, init_width_or_weight=60)

    def update(self, world: World, dt: float):
        # Clear table rows?
        # dpg.delete_item(self.table_tag, children_only=True)
        # Re-creating rows every frame is expensive.
        # But DPG doesn't have an easy "update cell" without tracking tags.
        # For < 50 agents it's fine.

        # We need to manage rows.
        # Let's use a simple approach: delete and recreate for now.
        if dpg.does_item_exist(self.table_tag):
             dpg.delete_item(self.table_tag, children_only=True)

        # Find entities with BrainComponent (and optionally StatsComponent)
        brains = world.get_components(BrainComponent)
        stats_map = world.get_components(StatsComponent)

        for entity_id, brain in brains.items():
            stats = stats_map.get(entity_id)

            # Prepare data
            entity_str = str(entity_id)[:8] # Short ID
            bt_status = "Inactive"
            if brain.root:
                bt_status = brain.root.status.value

            fps = f"{stats.fps:.1f}" if stats else "N/A"
            cpu = f"{stats.cpu_usage:.1f}%" if stats else "N/A"
            health = f"{stats.health:.0f}/{stats.max_health:.0f}" if stats else "N/A"
            stamina = f"{stats.stamina:.0f}/{stats.max_stamina:.0f}" if stats else "N/A"

            with dpg.table_row(parent=self.table_tag):
                dpg.add_text(entity_str)
                dpg.add_text(bt_status)
                dpg.add_text(fps)
                dpg.add_text(cpu)
                dpg.add_text(health)
                dpg.add_text(stamina)
                dpg.add_button(label="Focus", callback=self.on_focus, user_data=entity_id)

    def on_focus(self, sender, app_data, user_data):
        SelectionService.set_selected(user_data, "ENTITY")
