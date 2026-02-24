import moderngl
import glfw
import numpy as np
import glm
import os
from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase, EngineMode
from components.core import MeshComponent, MaterialComponent, CameraComponent
from components.spatial import TransformComponent
from assets.models.cube import get_cube_data

@register_system(phase=Phase.PERCEPTION)
class ModernGLRenderSystem(System):
    """
    Hardware-accelerated rendering system using ModernGL.
    
    When use_fbo=True (embedded in GUI), uses a standalone ModernGL context
    via an offscreen GLFW window. This avoids ALL context conflicts with DearPyGui,
    which manages its own OpenGL context independently.
    
    When use_fbo=False (standalone), uses a normal GLFW window.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        return cls._instance

    def __init__(self, use_fbo: bool = False):
        ModernGLRenderSystem._instance = self
        self.ctx = None
        self.window = None
        self.prog = None
        self.vao = None
        self.vbo = None
        self.initialized = False
        
        # FBO Support for Embedding
        self.use_fbo = use_fbo
        self.fbo = None
        self.fbo_texture = None
        self.fbo_depth = None
        self.fbo_data = None # Prepared for DPG
        
        # Resource cache
        self.meshes = {} # path -> vao
        self.shaders = {} # name -> program
        
        # Shared State for Raycasting/Picking
        self.last_proj = glm.mat4(1.0)
        self.last_view = glm.mat4(1.0)

    def _init_moderngl(self):
        if self.use_fbo:
            return self._init_offscreen()
        else:
            return self._init_window()

    def _init_offscreen(self):
        """
        Initialize a standalone ModernGL context for offscreen FBO rendering.
        This does NOT use GLFW and therefore cannot conflict with DearPyGui's context.
        Uses a hidden GLFW window purely as a GL context provider.
        """
        if not glfw.init():
            print("[Render] GLFW init failed")
            return False
        
        # Hints for a hidden, non-decorated context provider window
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.FOCUSED, glfw.FALSE)
        glfw.window_hint(glfw.FOCUS_ON_SHOW, glfw.FALSE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        self.window = glfw.create_window(1, 1, "OffscreenCtx", None, None)
        if not self.window:
            glfw.terminate()
            print("[Render] GLFW offscreen window creation failed")
            return False
        
        # Make current TEMPORARILY for initialization only
        glfw.make_context_current(self.window)
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        
        # Create FBO
        self.fbo_texture = self.ctx.texture((1280, 720), 4)
        self.fbo_depth = self.ctx.depth_renderbuffer((1280, 720))
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.fbo_texture],
            depth_attachment=self.fbo_depth
        )
        
        self._load_shader_and_mesh()
        
        # Release context NOW - DPG can freely use the thread
        glfw.make_context_current(None)
        
        self.initialized = True
        print("[Render] ModernGL Render System initialized (Offscreen FBO mode).")
        return True

    def _init_window(self):
        """Initialize a full GLFW window for standalone rendering."""
        if not glfw.init():
            return False
        
        glfw.window_hint(glfw.VISIBLE, glfw.TRUE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        self.window = glfw.create_window(1280, 720, "Serpentine Engine", None, None)
        if not self.window:
            glfw.terminate()
            return False
        
        glfw.make_context_current(self.window)
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        
        self._load_shader_and_mesh()
        
        self.initialized = True
        print("[Render] ModernGL Render System initialized (Window mode).")
        return True

    def _load_shader_and_mesh(self):
        """Load shaders and default mesh - called while context is current."""
        shader_path = "assets/shaders/default_lit.glsl"
        if os.path.exists(shader_path):
            with open(shader_path, 'r') as f:
                content = f.read()
                lines = content.splitlines()
                version_line = "#version 330"
                remaining_content = content
                if lines and lines[0].strip().startswith("#version"):
                    version_line = lines[0]
                    remaining_content = "\n".join(lines[1:])
                
                try:
                    self.prog = self.ctx.program(
                        vertex_shader=f"{version_line}\n#define VERTEX_SHADER\n{remaining_content}",
                        fragment_shader=f"{version_line}\n#define FRAGMENT_SHADER\n{remaining_content}",
                    )
                except Exception as e:
                    print(f"[Render] Shader compile error: {e}")
        
        cube_data = get_cube_data()
        self.vbo = self.ctx.buffer(cube_data)
        if self.prog:
            self.vao = self.ctx.vertex_array(self.prog, [
                (self.vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_texcoord_0')
            ])

    async def update(self, world: World, dt: float):
        if not self.initialized:
            if not self._init_moderngl():
                return

        if not self.use_fbo and glfw.window_should_close(self.window):
            glfw.terminate()
            self.initialized = False
            return

        if self.use_fbo:
            await self._update_offscreen(world)
        else:
            await self._update_window(world)

    async def _update_offscreen(self, world: World):
        """Render to FBO. Acquires and releases GLFW context each frame."""
        if not self.fbo:
            return
        try:
            # Acquire context for this frame
            glfw.make_context_current(self.window)
            self.fbo.use()
            self.ctx.clear(0.05, 0.05, 0.07)
            
            self._render_scene(world)
            
            # Read pixels for DPG
            raw_data = self.fbo.read(components=4, dtype='f1')
            if raw_data:
                img = np.frombuffer(raw_data, dtype=np.uint8).reshape((720, 1280, 4))
                self.fbo_data = img.astype(np.float32) / 255.0
        except Exception as e:
            print(f"[Render] Offscreen render error: {e}")
        finally:
            # ALWAYS release before DPG gets the thread back (TELEMETRY phase)
            try:
                glfw.make_context_current(None)
            except Exception:
                pass

    async def _update_window(self, world: World):
        """Render to a standard GLFW window."""
        try:
            self.ctx.screen.use()
            self.ctx.clear(0.05, 0.05, 0.07)
            self._render_scene(world)
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        except Exception as e:
            print(f"[Render] Window render error: {e}")

    def _render_scene(self, world: World):
        """Common scene rendering logic. Context must already be current."""
        if not self.prog or not self.vao:
            return
        
        # 1. Setup Camera
        camera_entities = world.get_entities_with(CameraComponent, TransformComponent)
        if not camera_entities:
            return
            
        cam_ent = list(camera_entities)[0]
        cam = world.get_component(cam_ent, CameraComponent)
        cam_transform = world.get_component(cam_ent, TransformComponent)
        
        if not cam or not cam_transform:
            return

        aspect = 1280 / 720
        proj = glm.perspective(glm.radians(cam.fov), aspect, cam.near, cam.far)
        cam_pos = glm.vec3(cam_transform.x, cam_transform.y, 10.0) 
        view = glm.lookAt(cam_pos, glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
        
        try:
            if 'm_proj' in self.prog: self.prog['m_proj'].write(proj)
            if 'm_view' in self.prog: self.prog['m_view'].write(view)
            if 'light_pos' in self.prog: self.prog['light_pos'].value = (5.0, 5.0, 5.0)
        except Exception as e:
            print(f"[Render] Uniform update error: {e}")

        self.last_proj = proj
        self.last_view = view

        # 2. Render Entities
        renderable_entities = world.get_entities_with(MeshComponent, TransformComponent, MaterialComponent)
        for entity in renderable_entities:
            transform = world.get_component(entity, TransformComponent)
            material = world.get_component(entity, MaterialComponent)
            
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(transform.x, transform.y, 0.0))
            
            try:
                if 'm_model' in self.prog: self.prog['m_model'].write(model)
                if 'diffuse_color' in self.prog:
                    self.prog['diffuse_color'].value = tuple(material.diffuse_color)
            except Exception:
                pass
            
            self.vao.render()
