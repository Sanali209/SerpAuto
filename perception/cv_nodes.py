import numpy
from typing import Dict, Any, Optional
import cv2
import os

try:
    import mss
except ImportError:
    mss = None

try:
    import onnxruntime as ort
except ImportError:
    ort = None

class ScreenCaptureNode:
    """Captures the main screen using mss and returns a NumPy array (BGRA)."""
    def __init__(self, monitor_index: int = 1):
        self.monitor_index = monitor_index

    def process(self, input_data: Any) -> Any:
        if mss is None:
            raise ImportError("mss library is required for screen capture.")
        with mss.mss() as sct:
            monitors = sct.monitors
            if self.monitor_index >= len(monitors):
                monitor = monitors[0] # Fallback to all monitors
            else:
                monitor = monitors[self.monitor_index]
            
            sct_img = sct.grab(monitor)
            return numpy.array(sct_img)

class CropNode:
    """Crops an image based on provided coordinates (x, y, w, h)."""
    def __init__(self, x: int = 0, y: int = 0, w: int = 100, h: int = 100):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def process(self, img: Any) -> Any:
        if not isinstance(img, numpy.ndarray):
            return img
        # Ensure coordinates are within bounds
        max_y, max_x = img.shape[:2]
        x1 = max(0, self.x)
        y1 = max(0, self.y)
        x2 = min(max_x, self.x + self.w)
        y2 = min(max_y, self.y + self.h)
        return img[y1:y2, x1:x2]

class GrayscaleNode:
    """Converts a BGR or BGRA image to Grayscale."""
    def process(self, img: Any) -> Any:
        if not isinstance(img, numpy.ndarray):
            return img
        
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            elif img.shape[2] == 3:
                return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

class YOLONode:
    """Processes an image using an ONNX YOLO model for high performance."""
    def __init__(self, model_path: str = "yolov8n.onnx", confidence: float = 0.5):
        self.model_path = model_path
        self.confidence = confidence
        self.session = None
        if ort is not None and os.path.exists(self.model_path):
            try:
                self.session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
            except Exception as e:
                print(f"Failed to load ONNX model: {e}")

    def process(self, img: Any) -> Dict[str, Any]:
        result_data = {"boxes": [], "labels": [], "scores": []}
        if self.session is None or img is None:
            return result_data

        # Preprocessing: Resize to 640x640 (standard YOLO)
        h, w = img.shape[:2]
        input_img = cv2.resize(img, (640, 640))
        if input_img.shape[2] == 4: # Remove alpha
            input_img = cv2.cvtColor(input_img, cv2.COLOR_BGRA2BGR)
        
        # BGR to RGB and Normalize
        input_img = input_img[:, :, ::-1].transpose(2, 0, 1) # HWC to CHW
        input_img = numpy.expand_dims(input_img, axis=0).astype(numpy.float32) / 255.0

        # Run Inference
        inputs = {self.session.get_inputs()[0].name: input_img}
        outputs = self.session.run(None, inputs)
        
        # Postprocessing (Simplified)
        # Note: YOLO output format varies by version; this is a generic placeholder
        # for a standard [1, 84, 8400] detection tensor.
        predictions = numpy.squeeze(outputs[0])
        # [84, 8400] -> [8400, 84]
        predictions = predictions.T
        
        for pred in predictions:
            score = pred[4:].max()
            if score > self.confidence:
                class_id = numpy.argmax(pred[4:])
                # Scaling back to original image size
                # YOLO output is center_x, center_y, width, height
                cx, cy, cw, ch = pred[:4]
                x1 = (cx - cw/2) * (w / 640)
                y1 = (cy - ch/2) * (h / 640)
                x2 = (cx + cw/2) * (w / 640)
                y2 = (cy + ch/2) * (h / 640)
                
                result_data["boxes"].append([float(x1), float(y1), float(x2), float(y2)])
                result_data["scores"].append(float(score))
                result_data["labels"].append(str(class_id)) # Add class names map if available

        return result_data

# Registry for automatic UI discovery
AVAILABLE_NODES = [
    ScreenCaptureNode,
    CropNode,
    GrayscaleNode,
    YOLONode
]
