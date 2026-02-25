try:
    from pydantic import BaseModel, ConfigDict
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel, ConfigDict

class BaseComponent(BaseModel):
    """
    Base class for all components in the ECS.
    Components are pure data containers.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
