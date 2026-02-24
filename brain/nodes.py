from typing import Any, Optional
import asyncio
import time
from brain.behavior_tree import BehaviorTreeNode, Status
from brain.adapter import BaseAIAdapter
from brain.adapters_impl import ContextBuilder
from components.core import BrainComponent, PerceptionComponent, MemoryComponent
from core.world import World

# --- Decorators ---

class Inverter(BehaviorTreeNode):
    """Inverts the status of the child node."""
    def __init__(self, child: BehaviorTreeNode):
        self.child = child

    async def tick(self, world: World, agent_id: Any) -> Status:
        status = await self.child.tick(world, agent_id)
        if status == Status.SUCCESS:
            return Status.FAILURE
        if status == Status.FAILURE:
            return Status.SUCCESS
        return Status.RUNNING

class Succeeder(BehaviorTreeNode):
    """Always returns SUCCESS, regardless of child outcome (unless RUNNING)."""
    def __init__(self, child: BehaviorTreeNode):
        self.child = child

    async def tick(self, world: World, agent_id: Any) -> Status:
        status = await self.child.tick(world, agent_id)
        if status == Status.RUNNING:
            return Status.RUNNING
        return Status.SUCCESS

class RepeatUntilFail(BehaviorTreeNode):
    """Repeats child until it fails."""
    def __init__(self, child: BehaviorTreeNode):
        self.child = child

    async def tick(self, world: World, agent_id: Any) -> Status:
        status = await self.child.tick(world, agent_id)
        if status == Status.FAILURE:
            return Status.SUCCESS
        if status == Status.RUNNING:
            return Status.RUNNING
        return Status.RUNNING # Keep repeating

# --- Utility Nodes ---

class WaitNode(BehaviorTreeNode):
    """Returns RUNNING for `seconds` duration."""
    def __init__(self, seconds: float):
        self.duration = seconds
        self.start_times = {} # entity_id -> float

    async def tick(self, world: World, agent_id: Any) -> Status:
        current_time = time.perf_counter()
        if agent_id not in self.start_times:
            self.start_times[agent_id] = current_time

        elapsed = current_time - self.start_times[agent_id]
        if elapsed >= self.duration:
            del self.start_times[agent_id]
            return Status.SUCCESS

        return Status.RUNNING

# --- Blackboard Nodes ---

class CheckBlackboardVariable(BehaviorTreeNode):
    """Checks a condition on the Blackboard."""
    def __init__(self, key: str, operator: str, value: Any):
        self.key = key
        self.operator = operator
        self.value = value

    async def tick(self, world: World, agent_id: Any) -> Status:
        memory = world.get_component(agent_id, MemoryComponent)
        if not memory:
            return Status.FAILURE

        actual = memory.blackboard.get(self.key)

        if self.operator == "==":
            return Status.SUCCESS if actual == self.value else Status.FAILURE
        elif self.operator == "!=":
            return Status.SUCCESS if actual != self.value else Status.FAILURE
        elif self.operator == ">":
            return Status.SUCCESS if actual > self.value else Status.FAILURE
        elif self.operator == "<":
            return Status.SUCCESS if actual < self.value else Status.FAILURE

        return Status.FAILURE

class SetBlackboardVariable(BehaviorTreeNode):
    """Sets a variable in the Blackboard."""
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value

    async def tick(self, world: World, agent_id: Any) -> Status:
        memory = world.get_component(agent_id, MemoryComponent)
        if memory:
            memory.blackboard[self.key] = self.value
            return Status.SUCCESS
        return Status.FAILURE

# --- AI Nodes ---

class LLMInferenceNode(BehaviorTreeNode):
    """
    A Behavior Tree node that triggers an async call via BaseAIAdapter 
    and writes the parsed result to the agent's blackboard.
    """
    def __init__(self, adapter: BaseAIAdapter, system_prompt: str = "You are an AI agent."):
        self.adapter = adapter
        self.system_prompt = system_prompt
        self.task = None

    async def tick(self, world: World, entity: Any) -> Status:
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
