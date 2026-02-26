from typing import Tuple, Optional, Any
try:
    import numpy as np
except ImportError:
    np = None

from serpentine.components.rendering import CameraComponent
from serpentine.components.standard import TransformComponent

class Ray:
    def __init__(self, origin: 'np.ndarray', direction: 'np.ndarray'):
        self.origin = origin
        self.direction = direction

    def __repr__(self):
        return f"Ray(origin={self.origin}, direction={self.direction})"

def create_perspective_matrix(fov, aspect, near, far):
    if not np: return None
    f = 1.0 / np.tan(np.radians(fov) / 2.0)
    nf = 1.0 / (near - far)
    m = np.zeros((4, 4), dtype='f4')
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) * nf
    m[2, 3] = (2 * far * near) * nf
    m[3, 2] = -1.0
    return m

def create_look_at(eye, target, up):
    if not np: return None
    z = eye - target
    z = z / np.linalg.norm(z)
    x = np.cross(up, z)
    x = x / np.linalg.norm(x)
    y = np.cross(z, x)

    view = np.eye(4, dtype='f4')
    view[0, :3] = x
    view[1, :3] = y
    view[2, :3] = z
    view[0, 3] = -np.dot(x, eye)
    view[1, 3] = -np.dot(y, eye)
    view[2, 3] = -np.dot(z, eye)
    return view

def get_ray_from_screen(
    camera: CameraComponent,
    camera_transform: TransformComponent,
    screen_x: float,
    screen_y: float,
    viewport_width: float,
    viewport_height: float
) -> Optional[Ray]:
    """
    Converts screen coordinates to a ray in world space.
    screen_x, screen_y are in pixels (top-left origin usually, but OpenGL uses bottom-left logic for NDC).
    We assume screen_x, screen_y are relative to the viewport top-left.
    """
    if not np:
        return None

    # Normalized Device Coordinates (NDC)
    # x: -1 to 1, y: -1 to 1
    ndc_x = (2.0 * screen_x) / viewport_width - 1.0
    ndc_y = 1.0 - (2.0 * screen_y) / viewport_height # Flip Y for OpenGL (bottom-left is -1, top-right is 1)

    # Clip coordinates
    clip_coords = np.array([ndc_x, ndc_y, -1.0, 1.0], dtype='f4')

    # Projection Matrix
    aspect = viewport_width / viewport_height
    proj_matrix = create_perspective_matrix(camera.fov, aspect, camera.near, camera.far)

    # View Matrix
    cam_pos = np.array([camera_transform.x, camera_transform.y, 10.0], dtype='f4') # Match RenderSystem
    target = np.array([camera_transform.x, camera_transform.y, 0.0], dtype='f4')
    up = np.array([0.0, 1.0, 0.0], dtype='f4')
    view_matrix = create_look_at(cam_pos, target, up)

    # Inverse Projection
    inv_proj = np.linalg.inv(proj_matrix)

    # Eye coordinates
    eye_coords = np.dot(inv_proj, clip_coords)
    eye_coords = np.array([eye_coords[0], eye_coords[1], -1.0, 0.0], dtype='f4')

    # Inverse View
    inv_view = np.linalg.inv(view_matrix)

    # World coordinates
    world_coords = np.dot(inv_view, eye_coords)
    ray_direction = np.array([world_coords[0], world_coords[1], world_coords[2]], dtype='f4')
    ray_direction = ray_direction / np.linalg.norm(ray_direction)

    return Ray(origin=cam_pos, direction=ray_direction)

def ray_box_intersection(ray: Ray, box_min: 'np.ndarray', box_max: 'np.ndarray') -> Optional[float]:
    """
    Returns distance to intersection or None.
    """
    if not np: return None

    t_min = (box_min - ray.origin) / ray.direction
    t_max = (box_max - ray.origin) / ray.direction

    t1 = np.minimum(t_min, t_max)
    t2 = np.maximum(t_min, t_max)

    t_near = np.max(t1)
    t_far = np.min(t2)

    if t_near > t_far or t_far < 0:
        return None

    return t_near

def ray_sphere_intersection(ray: Ray, center: 'np.ndarray', radius: float) -> Optional[float]:
    """
    Returns distance to intersection or None.
    """
    if not np: return None

    oc = ray.origin - center
    a = np.dot(ray.direction, ray.direction)
    b = 2.0 * np.dot(oc, ray.direction)
    c = np.dot(oc, oc) - radius * radius

    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return None
    else:
        dist = (-b - np.sqrt(discriminant)) / (2.0 * a)
        if dist < 0:
             dist = (-b + np.sqrt(discriminant)) / (2.0 * a)
             if dist < 0:
                 return None
        return dist
