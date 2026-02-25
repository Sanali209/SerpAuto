from uuid import UUID, uuid4
from typing import NewType

EntityID = NewType("EntityID", UUID)

def create_entity_id() -> EntityID:
    """Generates a new unique EntityID."""
    return EntityID(uuid4())
