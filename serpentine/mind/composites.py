from typing import List, Any, Optional
try:
    from pydantic import BaseModel
except ImportError:
    from serpentine.utils.pydantic_utils import BaseModel

from serpentine.core.registry import Registry
from serpentine.mind.core import BehaviorTreeNode, Status, Blackboard

@Registry.register_node(category="Composites", icon="➡️", description="Executes children sequentially until one fails.")
class Sequence(BehaviorTreeNode):
    def __init__(self, children: List[BehaviorTreeNode]):
        super().__init__()
        self.children = children
        self.current_child_index = 0

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        for i in range(self.current_child_index, len(self.children)):
            child = self.children[i]
            status = await child.tick(world, entity, blackboard)

            if status == Status.RUNNING:
                self.current_child_index = i
                return Status.RUNNING
            elif status == Status.FAILURE:
                self.current_child_index = 0
                return Status.FAILURE

        self.current_child_index = 0
        return Status.SUCCESS

    def reset(self):
        self.current_child_index = 0
        for child in self.children:
            child.reset()

@Registry.register_node(category="Composites", icon="❓", description="Executes children sequentially until one succeeds.")
class Selector(BehaviorTreeNode):
    def __init__(self, children: List[BehaviorTreeNode]):
        super().__init__()
        self.children = children
        self.current_child_index = 0

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        for i in range(self.current_child_index, len(self.children)):
            child = self.children[i]
            status = await child.tick(world, entity, blackboard)

            if status == Status.RUNNING:
                self.current_child_index = i
                return Status.RUNNING
            elif status == Status.SUCCESS:
                self.current_child_index = 0
                return Status.SUCCESS

        self.current_child_index = 0
        return Status.FAILURE

    def reset(self):
        self.current_child_index = 0
        for child in self.children:
            child.reset()

@Registry.register_node(category="Composites", icon="🔀", description="Executes children in parallel.")
class Parallel(BehaviorTreeNode):
    def __init__(self, children: List[BehaviorTreeNode]):
        super().__init__()
        self.children = children

    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        # Succeed on All, Fail on One
        any_failure = False
        all_success = True
        any_running = False

        for child in self.children:
            status = await child.tick(world, entity, blackboard)
            if status == Status.FAILURE:
                any_failure = True
            if status != Status.SUCCESS:
                all_success = False
            if status == Status.RUNNING:
                any_running = True

        if any_failure:
            return Status.FAILURE
        if any_running:
            return Status.RUNNING
        return Status.SUCCESS

    def reset(self):
        for child in self.children:
            child.reset()
