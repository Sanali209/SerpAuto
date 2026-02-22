from pydantic import BaseModel
import uuid

class BaseComponent(BaseModel):
    class Config:
        arbitrary_types_allowed = True
