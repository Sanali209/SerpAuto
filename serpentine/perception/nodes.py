from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, List
import logging

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

from serpentine.perception.types import Observation

logger = logging.getLogger(__name__)

class PerceptionNode(ABC):
    """Base class for perception processing nodes."""
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def process(self, input_data: Observation, **kwargs) -> Optional[Observation]:
        """
        Processes the input observation and returns a new observation.
        Returns None if processing fails or is not applicable.
        """
        pass

class CVNode(PerceptionNode):
    """Base class for Computer Vision nodes ensuring OpenCV is available."""
    def __init__(self, name: str):
        super().__init__(name)
        if cv2 is None or np is None:
            logger.warning(f"OpenCV or Numpy not available. {self.name} will be disabled.")

    def _validate_image(self, observation: Observation) -> Optional[Any]:
        if cv2 is None or np is None:
            return None

        if observation.data_type != "image":
            logger.warning(f"{self.name} received non-image data: {observation.data_type}")
            return None

        if not isinstance(observation.content, np.ndarray):
            logger.warning(f"{self.name} content is not numpy array.")
            return None

        return observation.content

class CropNode(CVNode):
    """Crops an image to a Region of Interest (ROI)."""
    def process(self, input_data: Observation, roi: Tuple[int, int, int, int] = None, **kwargs) -> Optional[Observation]:
        """
        roi: (x, y, w, h)
        """
        img = self._validate_image(input_data)
        if img is None:
            return None

        # If roi is not provided in kwargs, check metadata or default
        roi = roi or kwargs.get('roi')
        if not roi:
            return input_data  # No op

        x, y, w, h = roi
        h_img, w_img = img.shape[:2]

        # Ensure bounds
        x = max(0, min(x, w_img))
        y = max(0, min(y, h_img))
        w = max(0, min(w, w_img - x))
        h = max(0, min(h, h_img - y))

        cropped = img[y:y+h, x:x+w]

        return Observation(
            source_node=self.name,
            data_type="image",
            content=cropped,
            metadata={**input_data.metadata, "roi": roi, "original_size": (w_img, h_img)}
        )

class GrayscaleNode(CVNode):
    """Converts image to grayscale."""
    def process(self, input_data: Observation, **kwargs) -> Optional[Observation]:
        img = self._validate_image(input_data)
        if img is None:
            return None

        if len(img.shape) == 2:
            return input_data # Already gray

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        return Observation(
            source_node=self.name,
            data_type="image",
            content=gray,
            metadata={**input_data.metadata, "channels": 1}
        )

class TemplateMatchNode(CVNode):
    """Matches a template in the image."""
    def process(self, input_data: Observation, template: Any = None, threshold: float = 0.8, **kwargs) -> Optional[Observation]:
        img = self._validate_image(input_data)
        if img is None or template is None:
            return None

        # Convert to gray if needed for template matching usually
        # But we assume inputs match

        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        matches = []
        for pt in zip(*loc[::-1]):
            matches.append(pt)

        return Observation(
            source_node=self.name,
            data_type="template_matches",
            content=matches,
            metadata={"count": len(matches), "threshold": threshold}
        )

class OCRNode(CVNode):
    """Extracts text from image using Tesseract."""
    def process(self, input_data: Observation, config: str = '', **kwargs) -> Optional[Observation]:
        img = self._validate_image(input_data)
        if img is None:
            return None

        if pytesseract is None:
            logger.warning("pytesseract not installed.")
            return None

        text = pytesseract.image_to_string(img, config=config)

        return Observation(
            source_node=self.name,
            data_type="text",
            content=text.strip(),
            metadata={"config": config}
        )

class DOMParserNode(PerceptionNode):
    """Parses HTML/DOM content (Placeholder)."""
    def process(self, input_data: Observation, **kwargs) -> Optional[Observation]:
        if input_data.data_type != "dom":
            return None

        # Stub implementation
        dom_tree = {"tag": "body", "children": []} # Fake parsing

        return Observation(
            source_node=self.name,
            data_type="dom_tree",
            content=dom_tree,
            metadata={}
        )

class GridMapperNode(PerceptionNode):
    """Converts sensory data (e.g. image or internal) into a grid map."""
    def process(self, input_data: Observation, grid_size: Tuple[int, int] = (10, 10), **kwargs) -> Optional[Observation]:
        if np is None:
            logger.warning("Numpy not available for GridMapperNode.")
            return None

        # Implementation depends heavily on input type.
        # For now, let's assume it takes an 'internal_state' and maps it.

        if input_data.data_type == "internal_state":
            # Mock grid creation
            grid = np.zeros(grid_size, dtype=int)
            return Observation(
                source_node=self.name,
                data_type="grid",
                content=grid,
                metadata={"grid_size": grid_size}
            )

        return None
