import numpy as np
import uuid
import dearpygui.dearpygui as dpg

from core.system import System
from core.world import World
from core.registry import register_system, Registry
from core.engine_v2 import Phase, EngineMode
from components.core import MetadataComponent

try:
    from systems.auto_ui_builder import AutoUIBuilder
except ImportError:
    AutoUIBuilder = None

@register_system(phase=Phase.TELEMETRY)
class GUIDebugSystem(System):
    """
    Independent observation system rendering the "God Mode" dashboard via DearPyGui.
    """
    def __init__(self, engine=None, title="Serpentine Engine - God Mode", width=1440, height=900):
        self.engine = engine
        self.title = title
        self.width = width
        self.height = height
        self.dpg_initialized = False
        self.selected_entity = None
        
        self._init_dpg()
        
        from systems.gui_nodes import PipelineNodeEditor
        from systems.gui_systems import SystemInspector
        self.node_editor = PipelineNodeEditor()
        self.system_inspector = SystemInspector()
        
        self.swarm_messages = [] # For Swarm Sniffer

    def _init_dpg(self):
        dpg.create_context()
        # Keep basic docking, but avoid the experimental docking_space=True
        dpg.configure_app(docking=True)
        dpg.create_viewport(title=self.title, width=self.width, height=self.height)
        dpg.setup_dearpygui()
        
        # Setup Themes for Control Deck
        with dpg.theme(tag="play_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 150, 0))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 200, 0))
        with dpg.theme(tag="pause_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (150, 0, 0))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (200, 0, 0))
        with dpg.theme(tag="inactive_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60))
        
        # Texture Registry for CV Pipelines
        dpg.add_texture_registry(show=False, tag="texture_registry")
        # Initialize texture with the correct size (1280x720)
        dpg.add_dynamic_texture(width=1280, height=720, default_value=np.zeros((720, 1280, 4), dtype=np.float32).flatten(), tag="perception_texture", parent="texture_registry")
        
        # Build Workspace
        with dpg.window(tag="PrimaryWindow"):
            with dpg.menu_bar():
                with dpg.menu(label="Project"):
                    dpg.add_menu_item(label="Save Scene", callback=self._save_scene_cb)
                    dpg.add_menu_item(label="Load Scene", callback=self._load_scene_cb)
                    dpg.add_separator()
                    dpg.add_menu_item(label="Save Snapshot", callback=self._snapshot_cb)
                    dpg.add_menu_item(label="Load Snapshot", callback=self._load_snapshot_cb)
                    dpg.add_separator()
                    dpg.add_menu_item(label="Save Layout", callback=lambda: dpg.save_init_file("dpg_layout.ini"))
                    dpg.add_menu_item(label="Reset Engine", callback=self._reset_engine_cb)
                with dpg.menu(label="Windows"):
                    dpg.add_menu_item(label="Show Outliner", callback=lambda: dpg.show_item("OutlinerWindow"))
                    dpg.add_menu_item(label="Show Inspector", callback=lambda: dpg.show_item("InspectorWindow"))
                    dpg.add_menu_item(label="Show Viewport", callback=lambda: dpg.show_item("PerceptionWindow"))
                    dpg.add_menu_item(label="Show Swarm Sniffer", callback=lambda: dpg.show_item("SwarmSnifferWindow"))
                    dpg.add_menu_item(label="Show System Inspector", callback=lambda: dpg.show_item(self.system_inspector.window_tag))
                    dpg.add_menu_item(label="Show Dataset Inspector", callback=lambda: dpg.show_item("DatasetInspectorWindow"))
                    dpg.add_menu_item(label="Show Pipeline Node Editor", callback=lambda: dpg.show_item(self.node_editor.window_tag))
            
            # Pinned Control Deck (Overlay Window)
            with dpg.window(label="Control Deck", tag="ControlDeckWindow", no_close=True, no_collapse=True, width=700, height=40, pos=(310, 10), no_move=False):
                with dpg.group(horizontal=True):
                    # Play/Pause with color feedback
                    dpg.add_button(label="Play", width=60, tag="ctrl_play_btn", callback=self._play_cb)
                    dpg.add_button(label="Pause", width=60, tag="ctrl_pause_btn", callback=self._pause_cb)
                    dpg.add_button(label="Step", width=60, callback=self._step_cb)
                    dpg.add_text("| FPS: 0.0", tag="ctrl_fps_text")
                    dpg.add_text("| Mode:")
                    dpg.add_combo(items=[m.name for m in EngineMode], default_value="ARCHITECT", width=120)
                    dpg.add_text("Tick Rate:")
                    dpg.add_slider_int(min_value=1, max_value=60, default_value=60, width=120, callback=self._change_tick_rate_cb)
                
                # Teacher Mode Rec Button
                dpg.add_checkbox(label="[⏺ REC] Recording", tag="teacher_record_btn", callback=self._toggle_rec_cb)
                dpg.add_button(label="[🗑️ Drop Last Step]", callback=self._drop_step_cb)
            
            dpg.add_separator()
            
        # Left Panel: Outliner
        with dpg.window(label="World Outliner", tag="OutlinerWindow", width=300, height=400, pos=(0, 50)):
            with dpg.group(horizontal=True):
                dpg.add_button(label="[+ Add Entity]", callback=self._add_entity_cb)
                dpg.add_button(label="[🗑️ Destroy]", callback=self._destroy_entity_cb)
            
            dpg.add_separator()
            with dpg.tree_node(label="Entities", tag="outliner_tree", default_open=True):
                pass
            
            dpg.add_separator()
            dpg.add_text("Entity Name:", color=(150, 150, 150))
            dpg.add_input_text(tag="entity_rename_input", callback=self._on_entity_rename, width=-1)
        
        # Middle Panel: Viewport (renamed from Perception Monitor)
        with dpg.window(label="Engine Viewport", tag="PerceptionWindow", width=660, height=450, pos=(310, 50)):
            dpg.add_separator()
            with dpg.tab_bar():
                with dpg.tab(label="Main Viewport (3D/CV)"):
                    # The zero-copy image hook
                    with dpg.group():
                        dpg.add_image("perception_texture", tag="perception_image", width=640, height=360)
                        with dpg.item_handler_registry(tag="viewport_click_handler"):
                            dpg.add_item_clicked_handler(callback=self._on_viewport_click)
                        dpg.bind_item_handler_registry("perception_image", "viewport_click_handler")

                with dpg.tab(label="Raw Context (JSON Tree)"):
                    with dpg.group(tag="perc_tree_group"):
                        dpg.add_text("Select an entity with perception", color=(150, 150, 150))
                
        # Swarm Sniffer
        with dpg.window(label="Swarm Message Sniffer", tag="SwarmSnifferWindow", width=660, height=200, pos=(310, 505)):
            with dpg.tab_bar():
                with dpg.tab(label="Live Sniffer"):
                    dpg.add_text("Live inter-agent traffic:")
                    dpg.add_separator()
                    with dpg.child_window(tag="swarm_log_child", height=-1):
                        dpg.add_text("", tag="swarm_log_text")
                with dpg.tab(label="Traffic Matrix"):
                    with dpg.group(tag="swarm_matrix_group"):
                        dpg.add_text("No message traffic detected...", color=(150, 150, 150))

        # Right Panel: Inspector and Brain
        with dpg.window(label="Component Inspector", tag="InspectorWindow", width=400, height=600, pos=(970, 50)):
            with dpg.group(horizontal=True):
                # Dynamic component list
                avail_comps = list(Registry.get_all_components().keys())
                dpg.add_combo(items=avail_comps, tag="add_comp_combo", width=180)
                dpg.add_button(label="[+ Add]", callback=self._add_comp_cb)

            dpg.add_separator()
            with dpg.group(tag="inspector_group"):
                dpg.add_text("Select an entity to inspect", color=(150, 150, 150))
            
            dpg.add_separator()
            dpg.add_text("Brain & Memory (Blackboard)")
            with dpg.group(tag="brain_memory_group"):
                dpg.add_text("Select an entity...", color=(150, 150, 150))
                
            dpg.add_separator()
            dpg.add_text("Action Queue (Intervention)")
            with dpg.group(tag="action_queue_group"):
                dpg.add_text("Select an entity...", color=(150, 150, 150))

        # Dataset Inspector
        with dpg.window(label="Dataset Inspector", tag="DatasetInspectorWindow", width=300, height=200, pos=(970, 660)):
            dpg.add_text("Status: Stopped", tag="dataset_status_text")
            dpg.add_text("Buffer Size: 0", tag="dataset_buffer_text")
            dpg.add_text("Total Recorded: 0", tag="dataset_total_text")
            dpg.add_separator()
            dpg.add_text("Last Record:", color=(150, 150, 150))
            dpg.add_text("None", tag="dataset_last_action_text", wrap=0)
        
        dpg.set_primary_window("PrimaryWindow", True)
        dpg.show_viewport()
        self.dpg_initialized = True
        self._current_world = None
        self._last_selected_entity = None
        self._last_entity_count = 0

    def _add_entity_cb(self):
        if self._current_world:
            new_id = uuid.uuid4()
            self._current_world.add_entity(new_id)
            self.selected_entity = new_id

    def _destroy_entity_cb(self):
        if self._current_world and self.selected_entity:
            self._current_world.remove_entity(self.selected_entity)
            self.selected_entity = None
            dpg.delete_item("inspector_group", children_only=True)
            dpg.delete_item("brain_memory_group", children_only=True)
            dpg.delete_item("action_queue_group", children_only=True)

    def _add_comp_cb(self):
        if not self._current_world or not self.selected_entity:
            return
        
        comp_name = dpg.get_value("add_comp_combo")
        comp_cls = Registry.get_component(comp_name)
        if comp_cls:
            # Instantiate with defaults
            try:
                comp_inst = comp_cls()
                self._current_world.add_component(self.selected_entity, comp_inst)
                self._on_entity_select(self.selected_entity, self._current_world) # Refresh inspector
            except Exception as e:
                print(f"Failed to add component {comp_name}: {e}")

    def _remove_comp_cb(self, sender, app_data, user_data):
        comp_cls = user_data
        if self._current_world and self.selected_entity:
            self._current_world.remove_component(self.selected_entity, comp_cls)
            self._on_entity_select(self.selected_entity, self._current_world) # Refresh

    def _play_cb(self):
        if self.engine:
            self.engine.is_paused = False

    def _pause_cb(self):
        if self.engine:
            self.engine.is_paused = True

    def _step_cb(self):
        if self.engine:
            self.engine.is_paused = True
            self.engine._do_step = True

    def _change_tick_rate_cb(self, sender, app_data):
        if self.engine:
            self.engine.tick_rate = app_data

    def _snapshot_cb(self):
        if self._current_world:
            from systems.persistence import PersistenceSystem
            PersistenceSystem.snapshot_world(self._current_world, "snapshot.json")
            print("Snapshot saved.")

    def _load_snapshot_cb(self):
        if self._current_world:
            from systems.persistence import PersistenceSystem
            if self.engine:
                self.engine.is_paused = True
            PersistenceSystem.load_snapshot(self._current_world, "snapshot.json")
            print("Snapshot restored.")
            self.selected_entity = None
            dpg.delete_item("inspector_group", children_only=True)

    def _reset_engine_cb(self):
        if self._current_world:
            self._current_world.clear()
            self.selected_entity = None
            dpg.delete_item("inspector_group", children_only=True)
            print("Engine Reset.")

    def _save_scene_cb(self):
        if self._current_world:
            from core.scene import SceneManager
            SceneManager.save_scene("scene_output.json", self.engine)
            print("Scene saved to scene_output.json")

    def _load_scene_cb(self):
        if self._current_world:
            from core.scene import SceneManager
            SceneManager.load_scene("scene_output.json", self.engine)
            print("Scene loaded from scene_output.json")
            self.selected_entity = None

    def _on_entity_rename(self, sender, app_data):
        if self._current_world and self.selected_entity:
            from components.core import MetadataComponent
            meta = self._current_world.get_component(self.selected_entity, MetadataComponent)
            if not meta:
                # Lazy Injection
                meta = MetadataComponent(name=app_data)
                self._current_world.add_component(self.selected_entity, meta)
            else:
                meta.name = app_data
            print(f"Renamed entity to: {app_data}")

    async def update(self, world: World, dt: float):
        if not self.dpg_initialized:
            return
        
        self._current_world = world
        
        if dpg.is_dearpygui_running():
            # 1. Update Outliner (Only if entity count changes or forced)
            current_entities = list(world._entities)
            entity_count = len(current_entities)
            
            if entity_count != self._last_entity_count or not dpg.get_item_children("outliner_tree", 1):
                dpg.delete_item("outliner_tree", children_only=True)
                
                # Sort entities consistently (by Name or UUID)
                def get_sort_key(ent):
                    m = world.get_component(ent, MetadataComponent)
                    return (m.name.lower() if m else str(ent))
                
                sorted_entities = sorted(current_entities, key=get_sort_key)
                
                for entity in sorted_entities:
                    meta = world.get_component(entity, MetadataComponent)
                    display_name = meta.name if meta else f"Entity_{str(entity)[:8]}"
                    is_selected = (entity == self.selected_entity)
                    
                    dpg.add_selectable(
                        label=display_name, 
                        tag=f"outliner_{entity}", 
                        parent="outliner_tree",
                        callback=lambda s, a, u: self._on_entity_select(u, world),
                        user_data=entity,
                        default_value=is_selected
                    )
                self._last_entity_count = entity_count

            # Update selectable visual states without rebuilding the whole tree
            for entity in current_entities:
                tag = f"outliner_{entity}"
                if dpg.does_item_exist(tag):
                    is_selected = (entity == self.selected_entity)
                    dpg.set_value(tag, is_selected)
                    # Add visual indicator in label
                    meta = world.get_component(entity, MetadataComponent)
                    base_name = meta.name if meta else f"Entity_{str(entity)[:8]}"
                    label = f"[ > ] {base_name}" if is_selected else base_name
                    dpg.configure_item(tag, label=label)
            
            # Sync rename input
            if self.selected_entity:
                meta = world.get_component(self.selected_entity, MetadataComponent)
                current_name = meta.name if meta else f"Entity_{str(self.selected_entity)[:8]}"
                if not dpg.is_item_focused("entity_rename_input"):
                    dpg.set_value("entity_rename_input", current_name)
            
            # Sync Control Deck Colors via Themes
            if self.engine:
                if not self.engine.is_paused:
                    dpg.bind_item_theme("ctrl_play_btn", "play_theme")
                    dpg.bind_item_theme("ctrl_pause_btn", "inactive_theme")
                else:
                    dpg.bind_item_theme("ctrl_play_btn", "inactive_theme")
                    dpg.bind_item_theme("ctrl_pause_btn", "pause_theme")
            
            # 2. Update Monitors
            if self.selected_entity != self._last_selected_entity:
                self._refresh_live_monitors(world, force_rebuild=True)
                self._last_selected_entity = self.selected_entity
            else:
                self._refresh_live_monitors(world, force_rebuild=False)
                
            self._update_dataset_ui()
            self._update_swarm_sniffer()
            
            # 3. Update External Modules
            if dpg.is_item_visible(self.node_editor.window_tag):
                self.node_editor.update(world)
            
            if dpg.is_item_visible(self.system_inspector.window_tag):
                self.system_inspector.update(self.engine)
            
            # Sync FPS
            dpg.set_value("ctrl_fps_text", f"| FPS: {1.0/max(dt, 0.001):.1f}")
                    
            dpg.render_dearpygui_frame()
        else:
            dpg.destroy_context()

    def _update_swarm_sniffer(self):
        from systems.swarm import MessageRouterSystem
        history = MessageRouterSystem._history
        if not history:
            return

        # 1. Update Live Log
        log_str = ""
        for msg in history[-15:]: # Show last 15 messages
            sender = f"Node_{str(msg.sender_id)[:5]}"
            target = f"Node_{str(msg.target_id)[:5]}" if msg.target_id else "BROADCAST"
            log_str += f"[{target}] {sender} -> {msg.topic}: {str(msg.payload)[:20]}...\n"
        dpg.set_value("swarm_log_text", log_str)
        dpg.set_y_scroll("swarm_log_child", -1)

        # 2. Update Traffic Matrix (Simple table-based radar)
        if dpg.is_item_visible("SwarmSnifferWindow"):
            dpg.delete_item("swarm_matrix_group", children_only=True)
            traffic_counts = {} # (src, dst) -> count
            nodes = set()
            
            for msg in history[-100:]: # Look at recent window
                src = str(msg.sender_id)[:5]
                dst = str(msg.target_id)[:5] if msg.target_id else "BC"
                traffic_counts[(src, dst)] = traffic_counts.get((src, dst), 0) + 1
                nodes.add(src)
                nodes.add(dst)
            
            sorted_nodes = sorted(list(nodes))
            with dpg.table(header_row=True, parent="swarm_matrix_group", borders_innerH=True, borders_innerV=True, borders_outerH=True, borders_outerV=True):
                dpg.add_table_column(label="From \\ To")
                for node in sorted_nodes:
                    dpg.add_table_column(label=node)
                
                for src in sorted_nodes:
                    with dpg.table_row():
                        dpg.add_text(src, color=(0, 255, 255))
                        for dst in sorted_nodes:
                            count = traffic_counts.get((src, dst), 0)
                            color = (0, 255, 0) if count > 0 else (100, 100, 100)
                            dpg.add_text(str(count) if count > 0 else ".", color=color)

    def _on_viewport_click(self, sender, app_data):
        if not self._current_world:
            return

        # 1. Get mouse position relative to image
        # dpg.get_drawing_mouse_pos() or similar? 
        # For add_item_clicked_handler, app_data is usually the mouse button
        # We use dpg.get_item_pos and dpg.get_mouse_pos
        img_pos = dpg.get_item_pos("perception_image")
        mouse_pos = dpg.get_mouse_pos(local=False) # Screen space
        
        # Relative to image (top-left)
        rel_x = mouse_pos[0] - img_pos[0]
        rel_y = mouse_pos[1] - img_pos[1]

        # 2. Map to FBO Resolution (1280x720)
        # Image is displayed at (640, 360)
        scale_x = 1280 / 640
        scale_y = 720 / 360
        fbo_x = rel_x * scale_x
        fbo_y = rel_y * scale_y

        # 3. Find Raycast and Render systems
        from systems.raycast import RaycastSystem
        from systems.render_modern import ModernGLRenderSystem
        
        ray_sys = RaycastSystem.get_instance()
        render_sys = ModernGLRenderSystem.get_instance()
        
        if ray_sys and render_sys and render_sys.last_proj is not None:
            hit_entity = ray_sys.perform_raycast(
                self._current_world,
                (fbo_x, fbo_y),
                (1280, 720),
                render_sys.last_view,
                render_sys.last_proj
            )
            
            if hit_entity:
                self._on_entity_select(hit_entity, self._current_world)
                print(f"Viewport Selected: {hit_entity}")

    def _toggle_rec_cb(self, sender, app_data):
        try:
            from systems.advanced import DatasetLoggerSystem
            logger_sys = DatasetLoggerSystem.get_instance()
            if logger_sys:
                logger_sys.toggle_recording()
        except ImportError:
            pass

    def _drop_step_cb(self):
        try:
            from systems.advanced import DatasetLoggerSystem
            logger_sys = DatasetLoggerSystem.get_instance()
            if logger_sys:
                logger_sys.drop_last_step()
        except ImportError:
            pass

    def _update_dataset_ui(self):
        try:
            from systems.advanced import DatasetLoggerSystem
            logger_sys = DatasetLoggerSystem.get_instance()
            if logger_sys:
                status = "🔴 RECORDING" if logger_sys.is_recording else "Stopped"
                color = (255, 0, 0) if logger_sys.is_recording else (150, 150, 150)
                dpg.set_value("dataset_status_text", f"Status: {status}")
                dpg.configure_item("dataset_status_text", color=color)
                dpg.set_value("dataset_buffer_text", f"Buffer Size: {len(logger_sys.episode_buffer)}")
                dpg.set_value("dataset_total_text", f"Total Recorded: {logger_sys.record_count}")
                
                if logger_sys.episode_buffer:
                    last = logger_sys.episode_buffer[-1]
                    dpg.set_value("dataset_last_action_text", f"{last['action_type']}({last['action_params']})")
                else:
                    dpg.set_value("dataset_last_action_text", "None")
        except ImportError:
            pass

    def _refresh_live_monitors(self, world: World, force_rebuild: bool = False):
        # 1. Update Viewport
        try:
            # Prefer processed frame from selected entity
            show_fbo = True
            if self.selected_entity:
                from components.core import PerceptionComponent
                perc = world.get_component(self.selected_entity, PerceptionComponent)
                if perc and hasattr(perc, "processed_frame") and perc.processed_frame is not None:
                    frame = perc.processed_frame
                    # Ensure 4-channel float32 for DPG
                    if frame.dtype != np.float32:
                        frame = frame.astype(np.float32) / 255.0
                    
                    # Handle grayscale to color conversion
                    if len(frame.shape) == 2:
                        frame = np.stack([frame, frame, frame, np.ones_like(frame)], axis=-1)
                    elif frame.shape[2] == 3:
                        frame = np.concatenate([frame, np.ones((frame.shape[0], frame.shape[1], 1), dtype=np.float32)], axis=-1)
                    
                    # Resize if needed to match texture registry entry (1280x720)
                    # For performance, we'll just flatten and let DPG handle small size mismatches if possible, 
                    # but usually we should resize to 1280x720 or recreate texture.
                    # Standardizing to 1280x720 for now.
                    if frame.shape[:2] != (720, 1280):
                        import cv2
                        frame = cv2.resize(frame, (1280, 720))

                    dpg.set_value("perception_texture", frame.flatten())
                    show_fbo = False
            
            if show_fbo:
                from systems.render_modern import ModernGLRenderSystem
                render_sys = ModernGLRenderSystem.get_instance()
                if render_sys and render_sys.fbo_data is not None:
                    dpg.set_value("perception_texture", render_sys.fbo_data.flatten())
        except Exception as e:
            # print(f"[GUI] Texture update error: {e}")
            pass

        if not self.selected_entity:
            return
            
        perception_cls = Registry.get_component("PerceptionComponent")
        if perception_cls and world.get_component(self.selected_entity, perception_cls):
            perc = world.get_component(self.selected_entity, perception_cls)
            
            # Perception Tree Rebuild (Expensive, throttle or force)
            if force_rebuild:
                dpg.delete_item("perc_tree_group", children_only=True)
                
                def build_tree(data, parent):
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if isinstance(v, (dict, list)):
                                with dpg.tree_node(label=str(k), parent=parent):
                                    build_tree(v, dpg.last_item())
                            else:
                                dpg.add_text(f"{k}: {v}", parent=parent)
                    elif isinstance(data, list):
                        for idx, v in enumerate(data):
                            if isinstance(v, (dict, list)):
                                with dpg.tree_node(label=f"[{idx}]", parent=parent):
                                    build_tree(v, dpg.last_item())
                            else:
                                dpg.add_text(f"[{idx}]: {v}", parent=parent)
                
                build_tree(perc.raw_context, "perc_tree_group")
                dpg.add_text(f"\nVisible Entities: {len(perc.visible_entities)}", parent="perc_tree_group")

        # 2. Brain & Action Monitors (Rebuild only on selection)
        if force_rebuild:
            memory_cls = Registry.get_component("MemoryComponent")
            if memory_cls and world.get_component(self.selected_entity, memory_cls):
                mem = world.get_component(self.selected_entity, memory_cls)
                dpg.delete_item("brain_memory_group", children_only=True)
                AutoUIBuilder.build_ui_for_model(mem, "brain_memory_group")
                    
            action_cls = Registry.get_component("ActionBufferComponent")
            if action_cls and world.get_component(self.selected_entity, action_cls):
                act = world.get_component(self.selected_entity, action_cls)
                dpg.delete_item("action_queue_group", children_only=True)
                AutoUIBuilder.build_ui_for_model(act, "action_queue_group")

    def _on_entity_select(self, entity, world: World):
        self.selected_entity = entity
        dpg.delete_item("inspector_group", children_only=True)
        
        if AutoUIBuilder is None:
            dpg.add_text("AutoUIBuilder not loaded", parent="inspector_group")
            return

        components = []
        for c_type, c_dict in world._components.items():
            if entity in c_dict:
                components.append((c_type, c_dict[entity]))

        for comp_cls, comp_inst in components:
            with dpg.group(horizontal=True, parent="inspector_group"):
                header_id = dpg.add_collapsing_header(label=comp_cls.__name__, default_open=True)
                dpg.add_button(label="[X]", callback=self._remove_comp_cb, user_data=comp_cls)
            
            with dpg.group(parent=header_id):
                AutoUIBuilder.build_ui_for_model(comp_inst, dpg.last_item())
