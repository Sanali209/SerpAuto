import json
import httpx
from typing import Dict, Any, List
from brain.adapter import BaseAIAdapter, AIResponse
from components.core import PerceptionComponent, MemoryComponent

class ContextBuilder:
    """Service class that serializes Perception and Memory into a text/JSON prompt for LLMs."""
    @staticmethod
    def build_prompt(perception: PerceptionComponent, memory: MemoryComponent) -> str:
        context = {
            "perception": perception.raw_context,
            "visible_entities": perception.visible_entities,
            "blackboard": memory.blackboard,
            "recent_actions": memory.history[-5:] if memory.history else []
        }
        try:
            return json.dumps(context, indent=2)
        except Exception:
            return str(context)

class OpenAILikeAdapter(BaseAIAdapter):
    """Adapter for OpenAI-compatible APIs (GPT-4, Gemini)"""
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    async def generate_response(self, system_prompt: str, context_data: dict) -> AIResponse:
        # Placeholder for actual HTTP call
        return AIResponse(
            raw_text="mock response",
            parsed_actions=[],
            metadata={"model": "gpt-4"}
        )

class MicroserviceAdapter(BaseAIAdapter):
    """Adapter for lightweight, task-specific models (Koyeb/HF)"""
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    async def generate_response(self, system_prompt: str, context_data: dict) -> AIResponse:
        # Placeholder for fast inference call
        return AIResponse(
            raw_text="mock fast response",
            parsed_actions=[],
            metadata={"latency_ms": 10}
        )

class N8NWebhookAdapter(BaseAIAdapter):
    """Adapter for external workflow automation (n8n)"""
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def generate_response(self, system_prompt: str, context_data: dict) -> AIResponse:
        # Placeholder for webhook trigger
        return AIResponse(
            raw_text="workflow triggered",
            parsed_actions=[],
            metadata={"status": "queued"}
        )
