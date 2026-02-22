from typing import Dict, Any
from core.component import BaseComponent
from core.registry import register_component

@register_component()
class WebSessionComponent(BaseComponent):
    """Stores browser state for scraper"""
    current_url: str = ""
    cookies: Dict[str, str] = {}
    user_agent: str = ""

@register_component()
class DOMNodeComponent(BaseComponent):
    """HTML Element snapshot"""
    xpath: str = ""
    css_selector: str = ""
    attributes: Dict[str, str] = {} # href, class, id

@register_component()
class PayloadExtractionComponent(BaseComponent):
    """Container for collected data before sending to DB/FastAPI"""
    target_schema_name: str # e.g.: "PriceAlertSchema"
    extracted_data: Dict[str, Any] = {}
    validation_status: bool = False
