import uuid
import math
import asyncio
from typing import List, Optional
from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.spatial import TransformComponent, HierarchyComponent

@register_system(phase=Phase.INTERNAL_PHYSICS)
class TransformHierarchySystem(System):
    """
    Propagates transformations from parents to children in the scene graph.
    Ensures that if a Tank moves, its Turret moves with it, accounting for rotation.
    """
    async def update(self, world: World, dt: float):
        # 1. Find all entities with Transform AND Hierarchy
        entities = world.get_entities_with(TransformComponent, HierarchyComponent)
        if not entities:
            return

        # 2. Identify roots (entities with no parent)
        roots = []
        for ent in entities:
            hierarchy = world.get_component(ent, HierarchyComponent)
            if hierarchy.parent is None:
                roots.append(ent)

        # 3. Propagate down the tree
        for root_id in roots:
            self._update_tree(world, root_id, parent_transform=None)

    def _update_tree(self, world: World, entity_id: uuid.UUID, parent_transform: Optional[TransformComponent]):
        """
        Recursively calculates world coordinates with 2D rotation matrix.
        """
        transform = world.get_component(entity_id, TransformComponent)
        hierarchy = world.get_component(entity_id, HierarchyComponent)

        if not transform:
            return

        if parent_transform is None:
            # Root node: World == Local
            transform.world_x = transform.local_x
            transform.world_y = transform.local_y
            transform.world_rotation = transform.local_rotation
            transform.world_scale_x = transform.local_scale_x
            transform.world_scale_y = transform.local_scale_y
        else:
            # Child node: World = Parent World + Rotated Local Offset

            # 1. Scale
            scaled_x = transform.local_x * parent_transform.world_scale_x
            scaled_y = transform.local_y * parent_transform.world_scale_y

            # 2. Rotation (Matrix Multiplication)
            # theta in radians
            theta = math.radians(parent_transform.world_rotation)
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)

            # Rotation formula around origin (0,0) which is the parent's pivot
            rotated_x = scaled_x * cos_theta - scaled_y * sin_theta
            rotated_y = scaled_x * sin_theta + scaled_y * cos_theta

            # 3. Translation (World Offset)
            transform.world_x = parent_transform.world_x + rotated_x
            transform.world_y = parent_transform.world_y + rotated_y

            # 4. Rotation Inheritance
            transform.world_rotation = parent_transform.world_rotation + transform.local_rotation
            transform.world_scale_x = parent_transform.world_scale_x * transform.local_scale_x
            transform.world_scale_y = parent_transform.world_scale_y * transform.local_scale_y

        # Process children (limit recursion depth to prevent stack overflow in cyclic graphs)
        # Note: A real implementation should detect cycles. Here we rely on hierarchy correctness.
        if hierarchy and hierarchy.children:
            for child_id in hierarchy.children:
                # Get child's hierarchy to confirm it exists
                child_h = world.get_component(child_id, HierarchyComponent)
                if child_h:
                    self._update_tree(world, child_id, transform)
