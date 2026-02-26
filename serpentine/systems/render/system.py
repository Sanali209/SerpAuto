import time
import array
from typing import Optional, List, Tuple
import logging

try:
    import moderngl
    import numpy as np
except ImportError:
    moderngl = None
    np = None

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.components.standard import TransformComponent
from serpentine.components.rendering import CameraComponent, MeshComponent, MaterialComponent
from serpentine.systems.render.context import RenderContext
from serpentine.core.event_bus import GUIEventBus

logger = logging.getLogger(__name__)

# Basic Shaders
VERTEX_SHADER = """
#version 330

uniform mat4 Mvp;

in vec3 in_position;
in vec3 in_color;

out vec3 v_color;

void main() {
    v_color = in_color;
    gl_Position = Mvp * vec4(in_position, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330

in vec3 v_color;
out vec4 f_color;

void main() {
    f_color = vec4(v_color, 1.0);
}
"""

@Registry.register_system(phase=SystemPhase.TELEMETRY, modes=[EngineMode.ARCHITECT, EngineMode.TEACHER], priority=100)
class RenderSystem(System):
    """
    Renders the scene using ModernGL.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate)
        self.ctx: Optional[moderngl.Context] = None
        self.prog: Optional[moderngl.Program] = None
        self.vbo: Optional[moderngl.Buffer] = None
        self.ibo: Optional[moderngl.Buffer] = None
        self.vao: Optional[moderngl.VertexArray] = None
        self.width = 640
        self.height = 480
        self.initialized = False
        self.render_context = None

        # Cube vertices (x, y, z) + color (r, g, b)
        self.cube_vertices = np.array([
            -0.5, -0.5, -0.5, 0.0, 0.0, 0.0,
             0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
             0.5,  0.5, -0.5, 1.0, 1.0, 0.0,
            -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
            -0.5, -0.5,  0.5, 0.0, 0.0, 1.0,
             0.5, -0.5,  0.5, 1.0, 0.0, 1.0,
             0.5,  0.5,  0.5, 1.0, 1.0, 1.0,
            -0.5,  0.5,  0.5, 0.0, 1.0, 1.0,
        ], dtype='f4') if np else None

        # Cube indices
        self.cube_indices = np.array([
            0, 1, 2, 2, 3, 0,
            4, 5, 6, 6, 7, 4,
            4, 5, 1, 1, 0, 4,
            6, 7, 3, 3, 2, 6,
            5, 6, 2, 2, 1, 5,
            7, 4, 0, 0, 3, 7
        ], dtype='i4') if np else None

    def initialize(self):
        if not moderngl or not np:
            logger.warning("ModernGL or Numpy not found. Rendering disabled.")
            return

        try:
            self.render_context = RenderContext()
            self.render_context.init_context(self.width, self.height)
            self.ctx = self.render_context.ctx

            self.prog = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

            self.vbo = self.ctx.buffer(self.cube_vertices.tobytes())
            self.ibo = self.ctx.buffer(self.cube_indices.tobytes())

            vao_content = [
                (self.vbo, '3f 3f', 'in_position', 'in_color')
            ]
            self.vao = self.ctx.vertex_array(self.prog, vao_content, self.ibo)

            self.initialized = True
            logger.info("RenderSystem initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize RenderSystem: {e}")
            self.initialized = False

    async def update(self, world: World, dt: float) -> None:
        if not moderngl or not np:
            return

        if not self.initialized:
            self.initialize()
            if not self.initialized:
                return

        self.render_context.clear()

        # Find camera
        camera_entity = None
        camera_comp = None
        transform_comp = None

        entities = world.get_entities_with(CameraComponent, TransformComponent)
        if entities:
            camera_entity, (camera_comp, transform_comp) = entities[0]

        view_matrix = np.eye(4, dtype='f4')
        proj_matrix = np.eye(4, dtype='f4')

        if camera_comp and transform_comp:
            # Camera position
            cam_pos = np.array([transform_comp.x, transform_comp.y, 10.0], dtype='f4') # Hack: Assume Z=10
            target = np.array([transform_comp.x, transform_comp.y, 0.0], dtype='f4')
            up = np.array([0.0, 1.0, 0.0], dtype='f4')

            if not camera_comp.is_orthographic:
                fov = camera_comp.fov
                aspect = self.width / self.height
                near = camera_comp.near
                far = camera_comp.far
                proj_matrix = self.create_perspective_matrix(fov, aspect, near, far)
                view_matrix = self.create_look_at(cam_pos, target, up)
        else:
            # Default camera
            proj_matrix = self.create_perspective_matrix(60.0, self.width / self.height, 0.1, 100.0)
            view_matrix = self.create_look_at(np.array([0.0, 0.0, 10.0], dtype='f4'), np.array([0.0, 0.0, 0.0], dtype='f4'), np.array([0.0, 1.0, 0.0], dtype='f4'))

        vp = np.dot(proj_matrix, view_matrix) # P * V

        # Render entities
        for ent, (trans,) in world.get_entities_with(TransformComponent):
             if ent == camera_entity:
                 continue

             # Model Matrix
             model_matrix = np.eye(4, dtype='f4')
             # Translation
             # trans.x, trans.y are floats, convert to numpy float
             model_matrix[3, 0] = trans.x
             model_matrix[3, 1] = trans.y
             model_matrix[3, 2] = 0.0 # Z

             # Rotation (Z-axis)
             cos_r = np.cos(trans.rotation)
             sin_r = np.sin(trans.rotation)

             # Scaling Matrix
             S = np.diag([trans.scale_x, trans.scale_y, 1.0, 1.0]).astype('f4')

             # Rotation Matrix (around Z)
             R = np.eye(4, dtype='f4')
             R[0, 0] = cos_r
             R[0, 1] = -sin_r
             R[1, 0] = sin_r
             R[1, 1] = cos_r

             # Translation Matrix
             T = np.eye(4, dtype='f4')
             T[3, 0] = trans.x
             T[3, 1] = trans.y
             T[3, 2] = 0.0

             # Model Matrix = T * R * S
             model_matrix = T @ R @ S

             # MVP = P * V * M
             mvp = vp @ model_matrix

             # Send to shader (transpose for column-major)
             self.prog['Mvp'].write(np.ascontiguousarray(mvp.T).tobytes())
             self.vao.render()

        # Read pixels
        pixels = self.render_context.read_pixels()
        GUIEventBus.publish("RENDER_COMPLETE", {"width": self.width, "height": self.height, "pixels": pixels})

    def create_perspective_matrix(self, fov, aspect, near, far):
        f = 1.0 / np.tan(np.radians(fov) / 2.0)
        nf = 1.0 / (near - far)
        # OpenGL Perspective Matrix (Column-Major)
        # But we create it Row-Major here for Numpy
        # [ f/aspect, 0, 0, 0 ]
        # [ 0, f, 0, 0 ]
        # [ 0, 0, (far+near)*nf, -1 ]
        # [ 0, 0, (2*far*near)*nf, 0 ]
        # Since we transpose later, we should create it as logically intended (Row-Major representation of the matrix)

        m = np.zeros((4, 4), dtype='f4')
        m[0, 0] = f / aspect
        m[1, 1] = f
        m[2, 2] = (far + near) * nf
        m[2, 3] = (2 * far * near) * nf
        m[3, 2] = -1.0
        return m # This looks like standard GL proj matrix but checking indices carefully.
        # Standard:
        # 0,0 = f/aspect
        # 1,1 = f
        # 2,2 = (f+n)/(n-f)
        # 2,3 = (2fn)/(n-f)
        # 3,2 = -1
        # My code: (far+near)*nf = (f+n)/(n-f). Correct.
        # (2*far*near)*nf = 2fn/(n-f). Correct.
        # 3,2 = -1. Correct.
        # Wait, indices:
        # Row 2 (0-indexed) is 3rd row.
        # Col 3 (0-indexed) is 4th col.
        # Is that where 2fn/(n-f) goes?
        # Standard GL:
        # Col 2: [0, 0, C, -1]
        # Col 3: [0, 0, D, 0]
        # Where C = (f+n)/(n-f), D = 2fn/(n-f)
        # So in Row-Major:
        # Row 2: [0, 0, C, D]
        # Row 3: [0, 0, -1, 0]
        # My code:
        # m[2, 2] = C
        # m[2, 3] = D
        # m[3, 2] = -1
        # Correct.

    def create_look_at(self, eye, target, up):
        z = eye - target
        z = z / np.linalg.norm(z)
        x = np.cross(up, z)
        x = x / np.linalg.norm(x)
        y = np.cross(z, x)

        # Row-Major
        view = np.eye(4, dtype='f4')
        view[0, :3] = x
        view[1, :3] = y
        view[2, :3] = z
        view[0, 3] = -np.dot(x, eye)
        view[1, 3] = -np.dot(y, eye)
        view[2, 3] = -np.dot(z, eye)
        return view

    def shutdown(self):
        if self.initialized:
            self.render_context.release()
