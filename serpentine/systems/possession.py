from typing import Optional, Tuple
import logging

try:
    import numpy as np
except ImportError:
    np = None

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.core.event_bus import GUIEventBus
from serpentine.components.rendering import CameraComponent
from serpentine.components.standard import TransformComponent
from serpentine.components.physics import ColliderComponent
from serpentine.components.simulation import InputControlComponent
from serpentine.perception.components import ActionBufferComponent
from serpentine.systems.render.raycast import get_ray_from_screen, ray_box_intersection, ray_sphere_intersection

logger = logging.getLogger(__name__)

@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.ARCHITECT, EngineMode.TEACHER])
class PossessionSystem(System):
    """
    Handles selecting and possessing entities via mouse clicks in the viewport.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate)
        GUIEventBus.subscribe("VIEWPORT_CLICK", self.on_viewport_click)
        self.pending_click = None

    def on_viewport_click(self, data: dict):
        """
        Callback for viewport click events.
        data: {'x': float, 'y': float, 'width': float, 'height': float, 'button': int}
        """
        self.pending_click = data

    async def update(self, world: World, dt: float) -> None:
        if not self.pending_click:
            return

        if not np:
            logger.warning("Numpy not available, raycasting disabled.")
            self.pending_click = None
            return

        click_data = self.pending_click
        self.pending_click = None

        screen_x = click_data.get('x', 0)
        screen_y = click_data.get('y', 0)
        width = click_data.get('width', 1)
        height = click_data.get('height', 1)

        # Find active camera
        camera_entity = None
        camera_comp = None
        camera_transform = None

        for ent, (cam, trans) in world.get_entities_with(CameraComponent, TransformComponent):
            camera_entity = ent
            camera_comp = cam
            camera_transform = trans
            break

        if not camera_comp:
            # Create a default camera if none exists (fallback logic)
            # Actually, without a camera component in world, we can't raycast properly unless we assume a default view.
            # But RenderSystem uses a default view if no camera is found.
            # We should probably mirror that logic or fail.
            # For now, let's assume we need a camera entity.
            logger.warning("No CameraComponent found for raycasting.")
            return

        ray = get_ray_from_screen(camera_comp, camera_transform, screen_x, screen_y, width, height)
        if not ray:
            return

        # Find intersections
        closest_dist = float('inf')
        closest_entity = None

        for ent, (trans, collider) in world.get_entities_with(TransformComponent, ColliderComponent):
            dist = None

            # Simplified collision: AABB centered at transform position
            # Ideally we should apply rotation, but for AABB it's simpler.
            # Collider size is (w, h, d)

            if collider.shape == "box":
                half_size = np.array(collider.size) / 2.0
                center = np.array([trans.x, trans.y, 0.0]) # Assume Z=0 for 2D logic or use 3D transform if available

                # Apply offset
                offset = np.array(collider.offset)
                center += offset

                box_min = center - half_size
                box_max = center + half_size

                dist = ray_box_intersection(ray, box_min, box_max)

            elif collider.shape == "sphere":
                center = np.array([trans.x, trans.y, 0.0])
                offset = np.array(collider.offset)
                center += offset

                dist = ray_sphere_intersection(ray, center, collider.radius)

            if dist is not None and dist < closest_dist:
                closest_dist = dist
                closest_entity = ent

        if closest_entity:
            logger.info(f"Clicked on entity {closest_entity}")
            self.possess_entity(world, closest_entity)

    def possess_entity(self, world: World, target_entity):
        # Check if target is possessable (has ActionBufferComponent)
        if not world.has_component(target_entity, ActionBufferComponent):
             logger.info(f"Entity {target_entity} is not possessable (no ActionBufferComponent).")
             # Still select it? Maybe SelectionSystem handles selection.
             # PossessionSystem handles CONTROL.
             return

        # Disable current input control
        for ent, (input_ctrl,) in world.get_entities_with(InputControlComponent):
            if input_ctrl.enabled:
                input_ctrl.enabled = False
                logger.info(f"Released control of entity {ent}")

        # Enable target input control
        # Check if target already has InputControlComponent
        input_ctrl = world.get_component(target_entity, InputControlComponent)
        if input_ctrl:
            input_ctrl.enabled = True
        else:
            # Add component
            world.add_component(target_entity, InputControlComponent(enabled=True))

        logger.info(f"Possessed entity {target_entity}")
