import asyncio
from typing import Any, Optional
try:
    from pydantic import BaseModel
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel

from serpentine.core.registry import Registry
from serpentine.mind.core import BehaviorTreeNode, Status, Blackboard
from serpentine.mind.intent import ClickIntent, MoveIntent, KeyIntent
from serpentine.perception.components import ActionBufferComponent

@Registry.register_node(category="Actions", icon="⏳", description="Waits for a specified duration.")
class WaitNode(BehaviorTreeNode):
    class Params(BaseModel):
        duration: float

    def __init__(self, duration: float = 1.0):
        super().__init__(params=self.Params(duration=duration))
        self.duration = duration
        self.start_time = 0.0

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        if self.status != Status.RUNNING:
            self.start_time = asyncio.get_event_loop().time()
            self.status = Status.RUNNING
            return Status.RUNNING

        current_time = asyncio.get_event_loop().time()
        if current_time - self.start_time >= self.duration:
            self.status = Status.SUCCESS
            return Status.SUCCESS

        return Status.RUNNING

    def reset(self):
        self.status = Status.FAILURE
        self.start_time = 0.0

@Registry.register_node(category="Actions", icon="📝", description="Sets a variable in the blackboard.")
class SetBlackboardVariable(BehaviorTreeNode):
    class Params(BaseModel):
        key: str
        value: Any

    def __init__(self, key: str, value: Any):
        super().__init__(params=self.Params(key=key, value=value))
        self.key = key
        self.value = value

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        blackboard.set(self.key, self.value)
        return Status.SUCCESS

@Registry.register_node(category="Actions", icon="🖱️", description="Emits a ClickIntent.")
class ClickNode(BehaviorTreeNode):
    class Params(BaseModel):
        x: int
        y: int
        button: str = "left"

    def __init__(self, x: int, y: int, button: str = "left"):
        super().__init__(params=self.Params(x=x, y=y, button=button))
        self.x = x
        self.y = y
        self.button = button

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        buffer: Optional[ActionBufferComponent] = world.get_component(entity, ActionBufferComponent)
        if buffer:
            intent = ClickIntent(x=self.x, y=self.y, button=self.button)
            buffer.enqueue(intent)
            return Status.SUCCESS
        return Status.FAILURE

@Registry.register_node(category="Actions", icon="🖱️", description="Emits a MoveIntent.")
class MoveNode(BehaviorTreeNode):
    class Params(BaseModel):
        x: int
        y: int
        duration: float = 0.0

    def __init__(self, x: int, y: int, duration: float = 0.0):
        super().__init__(params=self.Params(x=x, y=y, duration=duration))
        self.x = x
        self.y = y
        self.duration = duration

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        buffer: Optional[ActionBufferComponent] = world.get_component(entity, ActionBufferComponent)
        if buffer:
            intent = MoveIntent(x=self.x, y=self.y, duration=self.duration)
            buffer.enqueue(intent)
            return Status.SUCCESS
        return Status.FAILURE

@Registry.register_node(category="Actions", icon="⌨️", description="Emits a KeyIntent.")
class KeyNode(BehaviorTreeNode):
    class Params(BaseModel):
        key: str
        action: str = "press"

    def __init__(self, key: str, action: str = "press"):
        super().__init__(params=self.Params(key=key, action=action))
        self.key = key
        self.action = action

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        buffer: Optional[ActionBufferComponent] = world.get_component(entity, ActionBufferComponent)
        if buffer:
            intent = KeyIntent(key=self.key, action=self.action)
            buffer.enqueue(intent)
            return Status.SUCCESS
        return Status.FAILURE
