from typing import Any
try:
    from pydantic import BaseModel
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel

from serpentine.core.registry import Registry
from serpentine.mind.core import BehaviorTreeNode, Status, Blackboard

@Registry.register_node(category="Decorators", icon="❗", description="Inverts the status of its child (Success -> Failure, Failure -> Success).")
class Inverter(BehaviorTreeNode):
    def __init__(self, child: BehaviorTreeNode):
        super().__init__()
        self.child = child

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        status = await self.child.tick(world, entity, blackboard)
        if status == Status.SUCCESS:
            return Status.FAILURE
        if status == Status.FAILURE:
            return Status.SUCCESS
        return status

    def reset(self):
        self.child.reset()

@Registry.register_node(category="Decorators", icon="✅", description="Always returns SUCCESS.")
class Succeeder(BehaviorTreeNode):
    def __init__(self, child: BehaviorTreeNode):
        super().__init__()
        self.child = child

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        status = await self.child.tick(world, entity, blackboard)
        if status == Status.RUNNING:
            return Status.RUNNING
        return Status.SUCCESS

    def reset(self):
        self.child.reset()

@Registry.register_node(category="Decorators", icon="🔄", description="Repeats child until it fails.")
class RepeatUntilFail(BehaviorTreeNode):
    def __init__(self, child: BehaviorTreeNode):
        super().__init__()
        self.child = child

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        status = await self.child.tick(world, entity, blackboard)
        if status == Status.FAILURE:
            return Status.SUCCESS # Completed loop
        if status == Status.RUNNING:
            return Status.RUNNING

        # If Success, we repeat (return RUNNING so next tick we run again)
        return Status.RUNNING

    def reset(self):
        self.child.reset()
