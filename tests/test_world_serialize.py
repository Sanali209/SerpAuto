import unittest
import uuid
from core.world import World
from core.component import BaseComponent
from pydantic import BaseModel

class TestComponent(BaseComponent):
    value: int
    uid: uuid.UUID

class TestWorldSerialize(unittest.TestCase):
    def test_serialize_returns_objects(self):
        """Verify that serialize() returns Python objects (like UUID), not strings."""
        w = World()
        e = w.add_entity()
        comp_uid = uuid.uuid4()
        w.add_component(e, TestComponent(value=123, uid=comp_uid))

        data = w.serialize()

        # Check components structure
        comp_data = data["components"]["TestComponent"][str(e)]

        # Verify UUID is preserved as object
        self.assertIsInstance(comp_data["uid"], uuid.UUID)
        self.assertEqual(comp_data["uid"], comp_uid)

if __name__ == '__main__':
    unittest.main()
