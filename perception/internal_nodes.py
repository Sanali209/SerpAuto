from typing import Any, Dict, List
import numpy as np
import uuid
from core.component import BaseComponent
from components.spatial import TransformComponent
from core.registry import register_component

try:
    import pytesseract
except ImportError:
    pytesseract = None

class OCRNode:
    """
    Extracts text from image data using Tesseract.
    """
    def __init__(self, lang: str = "eng"):
        self.lang = lang

    def process(self, img: Any) -> Dict[str, Any]:
        if pytesseract is None:
            print("[OCR] pytesseract not installed.")
            return {"text": "", "conf": 0.0}
        
        # Assume img is numpy array (OpenCV style)
        try:
            # Simple string extraction
            text = pytesseract.image_to_string(img, lang=self.lang)
            return {"text": text.strip()}
        except Exception as e:
            print(f"[OCR] Error: {e}")
            return {"text": "", "error": str(e)}

class GridMapperNode:
    """
    Converts a list of entities (transforms) into a 2D occupancy grid.
    """
    def __init__(self, grid_size: int = 10, cell_size: float = 1.0):
        self.grid_size = grid_size
        self.cell_size = cell_size

    def process(self, context: Dict[str, Any]) -> np.ndarray:
        """
        Expects context to contain a list of 'entities' with 'x' and 'y'.
        Returns a numpy grid (0 = empty, 1 = occupied).
        """
        grid = np.zeros((self.grid_size, self.grid_size), dtype=int)

        entities = context.get("visible_entities", [])
        for ent in entities:
            # Assuming ent is a dict of component data or similar
            if 'TransformComponent' in ent:
                t = ent['TransformComponent']
                gx = int(t['world_x'] / self.cell_size)
                gy = int(t['world_y'] / self.cell_size)

                if 0 <= gx < self.grid_size and 0 <= gy < self.grid_size:
                    grid[gy, gx] = 1 # Mark occupied

        return grid
