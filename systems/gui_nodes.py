import dearpygui.dearpygui as dpg
from core.registry import Registry
from systems.auto_ui_builder import AutoUIBuilder

class PipelineNodeEditor:
    """
    Visual DAG editor for Serpentine's Perception Pipeline.
    Displays nodes and allows real-time configuration of their parameters.
    """
    def __init__(self, window_tag="PipelineEditorWindow"):
        self.window_tag = window_tag
        self._last_node_count = -1 # Force initial build
        self._setup_window()

    def _setup_window(self):
        # 1. Main Window
        with dpg.window(label="Perception Pipeline Editor", tag=self.window_tag, width=600, height=400, pos=(400, 500)):
            # 2. Stable Menu Bar
            with dpg.menu_bar():
                with dpg.menu(label="Add Node"):
                    from perception.cv_nodes import AVAILABLE_NODES
                    for node_cls in AVAILABLE_NODES:
                        # Closure fix: use default argument to capture current node_cls
                        dpg.add_menu_item(label=node_cls.__name__, callback=lambda s, a, u: self._on_add_node_cb(u), user_data=node_cls)
            
            # 3. Stable Node Editor (children will be refreshed, but editor itself is stable)
            dpg.add_node_editor(tag="pipeline_node_editor", 
                               callback=self._link_callback, 
                               delink_callback=self._delink_callback,
                               minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_BottomRight)
        
        # 4. Stable Handlers (Global or Window scoped)
        with dpg.handler_registry(tag="pipeline_handlers"):
            dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Right, callback=self._on_right_click)
        
        # 5. Stable Context Menu Window (Invisible by default)
        with dpg.window(tag="node_context_menu", modal=False, show=False, no_title_bar=True, no_move=True, no_resize=True, width=180):
            from perception.cv_nodes import AVAILABLE_NODES
            for node_cls in AVAILABLE_NODES:
                dpg.add_button(label=f"+ {node_cls.__name__}", width=-1, callback=lambda s, a, u: self._on_add_node_cb(u), user_data=node_cls)
            dpg.add_separator()
            dpg.add_button(label="Close", width=-1, callback=lambda: dpg.hide_item("node_context_menu"))

    def _on_right_click(self):
        # Only show if the pipeline editor window or node editor is active/hovered
        if dpg.is_item_hovered(self.window_tag) or dpg.is_item_hovered("pipeline_node_editor"):
            pos = dpg.get_mouse_pos(local=False)
            dpg.set_item_pos("node_context_menu", pos)
            dpg.show_item("node_context_menu")
        else:
            dpg.hide_item("node_context_menu")

    def _on_add_node_cb(self, node_cls):
        from perception.pipeline import PerceptionPipelineSystem
        pipeline_sys = PerceptionPipelineSystem.get_instance()
        if pipeline_sys:
            try:
                # All nodes now have default constructors
                new_node = node_cls()
                pipeline_sys.nodes.append(new_node)
                print(f"[Pipeline] Added node: {node_cls.__name__}")
                dpg.hide_item("node_context_menu")
            except Exception as e:
                print(f"[Pipeline] Failed to add node {node_cls.__name__}: {e}")

    def _remove_node_cb(self, idx):
        from perception.pipeline import PerceptionPipelineSystem
        pipeline_sys = PerceptionPipelineSystem.get_instance()
        # idx is the logical index in the nodes list
        if pipeline_sys and 0 <= idx < len(pipeline_sys.nodes):
            removed = pipeline_sys.nodes.pop(idx)
            print(f"[Pipeline] Removed node: {removed.__class__.__name__}")

    def _link_callback(self, sender, app_data):
        # Visual link creation
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        print(f"[Pipeline] Visual Link Created: {app_data}")

    def _delink_callback(self, sender, app_data):
        dpg.delete_item(app_data)
        print(f"[Pipeline] Visual Link Deleted: {app_data}")

    def update(self, world):
        """Syncs the visual nodes with the actual PerceptionPipelineSystem."""
        from perception.pipeline import PerceptionPipelineSystem
        pipeline_sys = PerceptionPipelineSystem.get_instance()
        
        if not pipeline_sys:
            return

        # Check for structure changes (addition or removal)
        current_node_count = len(pipeline_sys.nodes)
        if current_node_count != self._last_node_count:
            # Rebuild children of the editor
            dpg.delete_item("pipeline_node_editor", children_only=True)
            
            for idx, node in enumerate(pipeline_sys.nodes):
                # Unique tag per slot to avoid collisions if nodes are reordered
                node_tag = f"p_node_slot_{idx}"
                with dpg.node(label=f"{idx}: {node.__class__.__name__}", parent="pipeline_node_editor", tag=node_tag):
                    with dpg.node_attribute(label="Input", attribute_type=dpg.mvNode_Attr_Input, tag=f"{node_tag}_in"):
                        dpg.add_text("Data Flow In")
                    
                    # Real-time config via AutoUI
                    if AutoUIBuilder:
                        from pydantic import BaseModel
                        if isinstance(node, BaseModel):
                            AutoUIBuilder.build_ui_for_model(node, dpg.last_item())
                    
                    with dpg.node_attribute(label="Output", attribute_type=dpg.mvNode_Attr_Output, tag=f"{node_tag}_out"):
                        dpg.add_text("Data Flow Out")
                        dpg.add_button(label="[Remove Node]", callback=lambda s, a, u: self._remove_node_cb(u), user_data=idx)

                # Linear horizontal layout
                dpg.set_item_pos(node_tag, [40 + idx * 260, 60])
            
            self._last_node_count = current_node_count
