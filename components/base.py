from pydantic import BaseModel

class BaseComponent(BaseModel):
    """Base class for all ECS components.

    Components are pure data containers.
    """
    pass
