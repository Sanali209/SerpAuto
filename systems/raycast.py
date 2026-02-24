import glm
import numpy as np
import uuid
from typing import Optional
from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.core import MeshComponent
from components.spatial import TransformComponent

@register_system(phase=Phase.INPUT)
class RaycastSystem(System):
    """
    Handles screen-to-world raycasting for selecting/interacting with 3D entities.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        return cls._instance

    def __init__(self):
        RaycastSystem._instance = self
        self.selected_entity: Optional[uuid.UUID] = None

    def screen_to_world_ray(self, mouse_pos: tuple, viewport_size: tuple, view_mat: glm.mat4, proj_mat: glm.mat4):
        """
        Converts 2D mouse coordinates to a 3D ray (origin, direction).
        mouse_pos: (x, y) in pixels (top-left origin)
        viewport_size: (w, h)
        """
        x, y = mouse_pos
        w, h = viewport_size

        # 1. Normalized Device Coordinates (NDC)
        # x: [0, w] -> [-1, 1]
        # y: [0, h] -> [1, -1] (flip Y)
        ndc_x = (2.0 * x) / w - 1.0
        ndc_y = 1.0 - (2.0 * y) / h

        # 2. Ray in Clip Space
        ray_clip = glm.vec4(ndc_x, ndc_y, -1.0, 1.0)

        # 3. Ray in Eye Space
        inv_proj = glm.inverse(proj_mat)
        ray_eye = inv_proj * ray_clip
        ray_eye = glm.vec4(ray_eye.x, ray_eye.y, -1.0, 0.0)

        # 4. Ray in World Space
        inv_view = glm.inverse(view_mat)
        ray_world = glm.vec3(inv_view * ray_eye)
        ray_world = glm.normalize(ray_world)

        # Origin is the camera position (extracted from view matrix)
        cam_pos = glm.vec3(inv_view[3])

        return cam_pos, ray_world

    def ray_aabb_intersection(self, ray_origin: glm.vec3, ray_dir: glm.vec3, box_min: glm.vec3, box_max: glm.vec3):
        """
        Slab method for Ray-AABB intersection.
        """
        t1 = (box_min.x - ray_origin.x) / (ray_dir.x if ray_dir.x != 0 else 1e-6)
        t2 = (box_max.x - ray_origin.x) / (ray_dir.x if ray_dir.x != 0 else 1e-6)
        t3 = (box_min.y - ray_origin.y) / (ray_dir.y if ray_dir.y != 0 else 1e-6)
        t4 = (box_max.y - ray_origin.y) / (ray_dir.y if ray_dir.y != 0 else 1e-6)
        t5 = (box_min.z - ray_origin.z) / (ray_dir.z if ray_dir.z != 0 else 1e-6)
        t6 = (box_max.z - ray_origin.z) / (ray_dir.z if ray_dir.z != 0 else 1e-6)

        tmin = max(max(min(t1, t2), min(t3, t4)), min(t5, t6))
        tmax = min(min(max(t1, t2), max(t3, t4)), max(t5, t6))

        if tmax < 0 or tmin > tmax:
            return False, 0
        return True, tmin

    async def update(self, world: World, dt: float):
        # This system usually acts on events or is called by the GUI
        pass

    def perform_raycast(self, world: World, mouse_pos: tuple, viewport_size: tuple, view_mat: glm.mat4, proj_mat: glm.mat4):
        origin, direction = self.screen_to_world_ray(mouse_pos, viewport_size, view_mat, proj_mat)
        
        best_entity = None
        min_dist = float('inf')

        renderables = world.get_entities_with(MeshComponent, TransformComponent)
        for entity in renderables:
            transform = world.get_component(entity, TransformComponent)
            # Simple AABB based on transform (assuming 1x1x1 cube for now since mesh data is static)
            # In a real engine, we'd use the mesh's actual bounds
            half_size = 0.5
            box_min = glm.vec3(transform.x - half_size, transform.y - half_size, -half_size)
            box_max = glm.vec3(transform.x + half_size, transform.y + half_size, half_size)

            hit, dist = self.ray_aabb_intersection(origin, direction, box_min, box_max)
            if hit and dist < min_dist:
                min_dist = dist
                best_entity = entity

        return best_entity
