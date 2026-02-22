from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

class AIResponse(BaseModel):
    raw_text: str
    parsed_actions: List[Dict[str, Any]] # e.g.: [{"action": "click", "x": 10, "y": 20}]
    metadata: Dict[str, Any] # Tokens, latency

class BaseAIAdapter(ABC):
    @abstractmethod
    async def generate_response(self, system_prompt: str, context_data: dict) -> AIResponse:
        """Main method called by Behavior Tree"""
        pass
