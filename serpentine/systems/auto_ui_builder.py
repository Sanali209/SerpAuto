from typing import Any, Dict, List, Type, get_type_hints, Union, Optional
from enum import Enum
import dearpygui.dearpygui as dpg
import inspect

try:
    from pydantic import BaseModel
    from pydantic.fields import FieldInfo
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, FieldInfo

class AutoUIBuilder:
    """
    Dynamically generates DearPyGui widgets from Pydantic models.
    """

    @classmethod
    def build_ui_for_model(cls, model: BaseModel, parent_tag: str, callback_prefix: str = ""):
        """
        Generates UI for a Pydantic model instance.
        """
        if not isinstance(model, BaseModel):
             dpg.add_text(f"Not a Pydantic Model: {type(model)}", parent=parent_tag)
             return

        # Pydantic v2
        if hasattr(model, 'model_fields'):
             fields = model.model_fields
        else:
             # Fallback for v1 or mock
             fields = model.__fields__

        for field_name, field_info in fields.items():
            if field_name.startswith('_'):
                continue

            # Check exclusion
            if hasattr(field_info, 'exclude') and field_info.exclude:
                continue

            # Get current value
            field_value = getattr(model, field_name)

            # Determine type
            field_type = type(field_value)
            # Try to get type hint
            hints = get_type_hints(model.__class__)
            if field_name in hints:
                hint = hints[field_name]
                # Unwrap Optional
                if hasattr(hint, "__origin__") and hint.__origin__ is Union:
                     args = hint.__args__
                     if type(None) in args:
                         # It's optional, get the non-None type
                         for arg in args:
                             if arg is not type(None):
                                 field_type = arg
                                 break
                else:
                    field_type = hint

            # Callback closure
            def make_callback(m, f_name, f_type):
                def cb(sender, app_data):
                    try:
                        # Convert if necessary (e.g. for Enum)
                        val = app_data
                        if isinstance(f_type, type) and issubclass(f_type, Enum):
                            val = f_type[app_data]
                        setattr(m, f_name, val)
                    except Exception as e:
                        print(f"Error updating {f_name}: {e}")
                return cb

            callback = make_callback(model, field_name, field_type)
            tag = f"{callback_prefix}{parent_tag}_{field_name}"

            with dpg.group(horizontal=True, parent=parent_tag):
                dpg.add_text(f"{field_name}:")

                # Widget selection logic
                if field_type is str:
                    dpg.add_input_text(default_value=field_value, callback=callback, width=-1)
                elif field_type is int:
                    dpg.add_drag_int(default_value=field_value, callback=callback, width=-1)
                elif field_type is float:
                    dpg.add_drag_float(default_value=field_value, callback=callback, width=-1)
                elif field_type is bool:
                    dpg.add_checkbox(default_value=field_value, callback=callback)
                elif isinstance(field_type, type) and issubclass(field_type, Enum):
                    items = [e.name for e in field_type]
                    current_val = field_value.name if isinstance(field_value, Enum) else str(field_value)
                    dpg.add_combo(items=items, default_value=current_val, callback=callback, width=-1)
                elif isinstance(field_value, BaseModel):
                    with dpg.tree_node(label=field_name):
                        cls.build_ui_for_model(field_value, dpg.last_item(), f"{tag}_")
                elif isinstance(field_value, dict):
                     with dpg.tree_node(label=f"{field_name} (Dict)"):
                        dpg.add_text("Dict editing not fully supported yet.")
                elif isinstance(field_value, list):
                     with dpg.tree_node(label=f"{field_name} (List)"):
                        dpg.add_text(f"List with {len(field_value)} items.")
                else:
                    dpg.add_text(f"{field_value} ({type(field_value).__name__})")
