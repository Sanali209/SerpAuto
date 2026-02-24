import unittest
import numpy as np
from perception.cv_nodes import CropNode, GrayscaleNode

class TestPerceptionCV(unittest.TestCase):
    def test_crop_node(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[10:20, 10:20] = 255
        
        node = CropNode(x=10, y=10, w=10, h=10)
        cropped = node.process(img)
        
        self.assertEqual(cropped.shape, (10, 10, 3))
        self.assertTrue(np.all(cropped == 255))

    def test_grayscale_node(self):
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        img[:, :] = [100, 100, 100] # BGR
        
        node = GrayscaleNode()
        gray = node.process(img)
        
        self.assertEqual(len(gray.shape), 2)
        self.assertEqual(gray[0, 0], 100)

if __name__ == '__main__':
    unittest.main()
