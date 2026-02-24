import typing
import enum
import dearpygui.dearpygui as dpg
from pydantic import BaseModel

class AutoUIBuilder:
    """Generates DearPyGui widgets dynamically from Pydantic models."""
    
    @classmethod
    def build_ui_for_model(cls, model: BaseModel, parent_tag: int | str):
        """Builds UI elements for a given Pydantic model instance and binds callbacks."""
        
        for field_name, field_info in model.model_fields.items():
            # Skip fields marked as internal/excluded
            if field_info.exclude:
                continue
                
            field_type = field_info.annotation
            value = getattr(model, field_name)

            def create_callback(model_ref, f_name):
                def callback(sender, app_data, user_data):
                    setattr(model_ref, f_name, app_data)
                return callback

            # Handle Enums
            if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
                items = [e.name for e in field_type]
                default_name = value.name if value else (items[0] if items else "")
                
                def enum_callback(model_ref, f_name, enum_cls):
                    def callback(sender, app_data, user_data):
                        setattr(model_ref, f_name, enum_cls[app_data])
                    return callback
                    
                dpg.add_combo(items=items, default_value=default_name, label=field_name, 
                              callback=enum_callback(model, field_name, field_type), parent=parent_tag)
                continue

            # Handle Nested Pydantic Models (Recursion)
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                with dpg.tree_node(label=field_name, parent=parent_tag):
                    if value is None:
                        dpg.add_text("None", color=(150, 150, 150))
                    else:
                        cls.build_ui_for_model(value, dpg.last_item())
                continue

            # Handle Complex Typing Structures (Dict, List, Optional)
            origin = typing.get_origin(field_type)
            if origin is not None:
                with dpg.tree_node(label=f"{field_name} ({getattr(origin, '__name__', str(origin))})", parent=parent_tag):
                    if origin is dict:
                        if value:
                            for k, v in value.items():
                                with dpg.group(horizontal=True):
                                    dpg.add_text(f"{k}:", color=(200, 200, 200))
                                    
                                    # Create dynamic callbacks for dict values
                                    def create_dict_callback(d_obj, key):
                                        def callback(sender, app_data):
                                            d_obj[key] = app_data
                                        return callback

                                    # Heuristic type detection for dict values
                                    if isinstance(v, float):
                                        dpg.add_drag_float(default_value=v, width=100, callback=create_dict_callback(value, k))
                                    elif isinstance(v, int):
                                        dpg.add_drag_int(default_value=v, width=100, callback=create_dict_callback(value, k))
                                    elif isinstance(v, bool):
                                        dpg.add_checkbox(default_value=v, callback=create_dict_callback(value, k))
                                    elif isinstance(v, str):
                                        dpg.add_input_text(default_value=v, width=150, callback=create_dict_callback(value, k))
                                    else:
                                        dpg.add_text(str(v))
                        else:
                            dpg.add_text("Empty Dict", color=(150, 150, 150))
                    elif origin is list:
                        if value:
                            for idx, item in enumerate(value):
                                dpg.add_text(f"[{idx}] {item}")
                        else:
                            dpg.add_text("Empty List", color=(150, 150, 150))
                    elif origin is typing.Union:
                        if value is None:
                            dpg.add_text("None", color=(150, 150, 150))
                        else:
                            dpg.add_text(str(value))
                continue

            # Basic primitive type mapping with Live Binding
            if field_type == int:
                dpg.add_drag_int(label=field_name, default_value=value or 0, callback=create_callback(model, field_name), parent=parent_tag)
            elif field_type == float:
                dpg.add_drag_float(label=field_name, default_value=value or 0.0, callback=create_callback(model, field_name), parent=parent_tag)
            elif field_type == bool:
                dpg.add_checkbox(label=field_name, default_value=bool(value), callback=create_callback(model, field_name), parent=parent_tag)
            elif field_type == str:
                dpg.add_input_text(label=field_name, default_value=value or "", callback=create_callback(model, field_name), parent=parent_tag)
            else:
                dpg.add_text(f"{field_name} (unsupported: {field_type})", color=(150, 50, 50), parent=parent_tag)
