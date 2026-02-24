from typing import Dict, Any, List
from core.component import BaseComponent

class PerceptionNode:
    """Base class for all perception processing nodes."""
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return context

class DOMParserNode:
    """Placeholder for DOM Extraction Logic"""
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Would extract data via XPath/CSS
        return context

class OCRNode:
    """Placeholder for Text Extraction (Docling/Tesseract)"""
    def process(self, image_data: Any) -> str:
        return "extracted text"

class GridMapperNode:
    """Placeholder for NavGrid Generation"""
    def process(self, perception_data: Dict[str, Any]) -> List[List[int]]:
        # Would return 2D grid
        return [[0, 0], [0, 0]]

class StateBuilderNode:
    """Aggregates outputs from other perception nodes into a single JSON representation."""
    def process(self, context: Dict[str, Any]) -> str:
        import json
        
        # Serialize only primitive types and standard collections from the context
        serializable_context = {}
        for k, v in context.items():
            if isinstance(v, (dict, list, str, int, float, bool, type(None))):
                serializable_context[k] = v
            else:
                # Optionally convert numpy arrays or other objects if needed
                serializable_context[k] = str(type(v))
                
        try:
            return json.dumps(serializable_context, indent=2)
        except Exception as e:
            return f"Error serializing state: {e}"
