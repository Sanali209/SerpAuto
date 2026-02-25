from abc import ABC, abstractmethod
import asyncio
from typing import Any, Dict, Optional
try:
    from pydantic import BaseModel
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel

from serpentine.core.registry import Registry
from serpentine.mind.core import BehaviorTreeNode, Status, Blackboard

class AIAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> str:
        pass

class MockAdapter(AIAdapter):
    """Mock adapter for testing."""
    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> str:
        await asyncio.sleep(0.1) # Simulate network delay
        return f"Mock response to: {prompt}"

@Registry.register_node(category="Cognition", icon="🧠", description="Queries an LLM via an AI Adapter.")
class LLMInferenceNode(BehaviorTreeNode):
    class Params(BaseModel):
        prompt_template: str
        output_key: str = "llm_response"

    def __init__(self, prompt_template: str, output_key: str = "llm_response", adapter: Optional[AIAdapter] = None):
        super().__init__(params=self.Params(prompt_template=prompt_template, output_key=output_key))
        self.prompt_template = prompt_template
        self.output_key = output_key
        self.adapter = adapter
        self.task: Optional[asyncio.Task] = None

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        if not self.adapter:
            # Attempt to use a default mock adapter if none provided, for safety/testing
            # Or return Failure. Let's return Failure and log (if logger available)
            return Status.FAILURE

        if self.task and not self.task.done():
            return Status.RUNNING

        if self.task and self.task.done():
            try:
                result = self.task.result()
                blackboard.set(self.output_key, result)
                self.task = None
                return Status.SUCCESS
            except Exception:
                self.task = None
                return Status.FAILURE

        # Start new task
        context = blackboard.data
        try:
            # Simple python format string
            prompt = self.prompt_template.format(**context)
        except KeyError:
            # If keys missing, just use raw template or partial format?
            # Let's use raw template to avoid crash
            prompt = self.prompt_template

        self.task = asyncio.create_task(self.adapter.generate(prompt, context))
        return Status.RUNNING

    def reset(self):
        if self.task and not self.task.done():
            self.task.cancel()
        self.task = None
