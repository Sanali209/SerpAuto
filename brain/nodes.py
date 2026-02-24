from typing import Any
from brain.behavior_tree import BehaviorTreeNode, Status
from brain.adapter import BaseAIAdapter
from brain.adapters_impl import ContextBuilder
from components.core import BrainComponent, PerceptionComponent, MemoryComponent
from core.world import World
import asyncio

class LLMInferenceNode(BehaviorTreeNode):
    """
    A Behavior Tree node that triggers an async call via BaseAIAdapter 
    and writes the parsed result to the agent's blackboard.
    """
    def __init__(self, adapter: BaseAIAdapter, system_prompt: str = "You are an AI agent."):
        self.adapter = adapter
        self.system_prompt = system_prompt
        self.task = None

    def execute(self, world: World, entity: Any) -> Status:
        brain = world.get_component(entity, BrainComponent)
        perception = world.get_component(entity, PerceptionComponent)
        memory = world.get_component(entity, MemoryComponent)

        if brain is None or perception is None or memory is None:
            return Status.FAILURE

        # If already waiting, check if task is done
        if brain.status == "WAITING_LLM" and self.task is not None:
            if self.task.done():
                try:
                    response = self.task.result()
                    # Write result back to memory
                    memory.blackboard["last_llm_response"] = response.raw_text
                    if response.parsed_actions:
                        memory.blackboard["parsed_actions"] = response.parsed_actions
                        # Actor-Learner Sync: Store A_t
                        brain.last_action = response.parsed_actions[0]
                    
                    brain.status = "IDLE"
                    self.task = None
                    return Status.SUCCESS
                except Exception as e:
                    print(f"LLM Inference failed: {e}")
                    brain.status = "IDLE"
                    self.task = None
                    return Status.FAILURE
            else:
                return Status.RUNNING
        
        # Start new task
        if brain.status == "IDLE" or brain.status == "RUNNING_BT":
            context_string = ContextBuilder.build_prompt(perception, memory)
            # Actor-Learner Sync: Store S_t
            brain.last_state = context_string
            # Create async task
            self.task = asyncio.create_task(
                self.adapter.generate_response(self.system_prompt, {"context": context_string})
            )
            brain.status = "WAITING_LLM"
            return Status.RUNNING

        return Status.FAILURE
