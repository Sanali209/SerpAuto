from typing import List, Literal, Tuple
from core.component import BaseComponent

class GridPositionComponent(BaseComponent):
    """Position on the 2D grid"""
    x: int
    y: int

class SnakeBodyComponent(BaseComponent):
    """Tail segments queue"""
    body_segments: List[Tuple[int, int]] = []
    length: int = 3

# Reusing ColliderComponent from internal.py, but strictly defining types for Snake
# actually we can just use the existing one but maybe we want to extend it for clarity
# or just rely on 'type' field convention.
# For this sample, let's subclass or just use standard components.
# The design doc says: class ColliderComponent(BaseComponent): type: Literal[...]
# But components/internal.py defined it with shape/size.
# Let's make a specific component for Snake Game Logic metadata to avoid conflicts.

class SnakeColliderComponent(BaseComponent):
    """Tag for collision logic in Snake"""
    type: Literal["head", "body", "apple", "wall"]
