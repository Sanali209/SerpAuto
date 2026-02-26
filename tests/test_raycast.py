import unittest
import sys
from unittest.mock import MagicMock

# Mock dearpygui before importing anything else
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()

try:
    import numpy as np
except ImportError:
    np = None

from serpentine.systems.render.raycast import Ray, ray_box_intersection, ray_sphere_intersection

class TestRaycast(unittest.TestCase):
    def setUp(self):
        if not np:
            self.skipTest("Numpy not installed")

    def test_ray_box_intersection(self):
        # Ray pointing at box
        origin = np.array([0.0, 0.0, 10.0])
        direction = np.array([0.0, 0.0, -1.0])
        ray = Ray(origin, direction)

        box_min = np.array([-1.0, -1.0, -1.0])
        box_max = np.array([1.0, 1.0, 1.0])

        dist = ray_box_intersection(ray, box_min, box_max)
        self.assertIsNotNone(dist)
        self.assertAlmostEqual(dist, 9.0) # Should hit at z=1.0. 10 - 1 = 9.

    def test_ray_box_miss(self):
        # Ray pointing away
        origin = np.array([0.0, 0.0, 10.0])
        direction = np.array([1.0, 0.0, 0.0])
        ray = Ray(origin, direction)

        box_min = np.array([-1.0, -1.0, -1.0])
        box_max = np.array([1.0, 1.0, 1.0])

        dist = ray_box_intersection(ray, box_min, box_max)
        self.assertIsNone(dist)

    def test_ray_sphere_intersection(self):
        # Ray pointing at sphere
        origin = np.array([0.0, 0.0, 10.0])
        direction = np.array([0.0, 0.0, -1.0])
        ray = Ray(origin, direction)

        center = np.array([0.0, 0.0, 0.0])
        radius = 1.0

        dist = ray_sphere_intersection(ray, center, radius)
        self.assertIsNotNone(dist)
        self.assertAlmostEqual(dist, 9.0)

    def test_ray_sphere_miss(self):
        # Ray pointing away
        origin = np.array([0.0, 0.0, 10.0])
        direction = np.array([1.0, 0.0, 0.0])
        ray = Ray(origin, direction)

        center = np.array([0.0, 0.0, 0.0])
        radius = 1.0

        dist = ray_sphere_intersection(ray, center, radius)
        self.assertIsNone(dist)

if __name__ == '__main__':
    unittest.main()
