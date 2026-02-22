from typing import Dict, Any
from core.component import BaseComponent

class WebSessionComponent(BaseComponent):
    """Stores browser state for scraper"""
    current_url: str = ""
    cookies: Dict[str, str] = {}
    user_agent: str = ""

class DOMNodeComponent(BaseComponent):
    """HTML Element snapshot"""
    xpath: str = ""
    css_selector: str = ""
    attributes: Dict[str, str] = {} # href, class, id

class PayloadExtractionComponent(BaseComponent):
    """Container for collected data before sending to DB/FastAPI"""
    target_schema_name: str # e.g.: "PriceAlertSchema"
    extracted_data: Dict[str, Any] = {}
    validation_status: bool = False
