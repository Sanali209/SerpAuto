import asyncio
import glm
import time
from core.engine_v2 import SerpentineEngineV2, EngineMode, Phase
from core.registry import Registry
from components.core import MeshComponent, MaterialComponent, CameraComponent
from components.spatial import TransformComponent

# Import systems to ensure registration
import systems.render_modern
import systems.gui
import systems.auto_ui_builder

async def main():
    print("Initializing God Mode + 3D Viewport Verification...")
    
    # We use ARCHITECT mode to get the GUI
    engine = SerpentineEngineV2(mode=EngineMode.ARCHITECT)
    world = engine.world
    
    # 1. Add ModernGL Render System (FBO Mode)
    from systems.render_modern import ModernGLRenderSystem
    render_sys = ModernGLRenderSystem(use_fbo=True)
    engine.add_system(render_sys, phase=Phase.TELEMETRY)
    
    # 2. Add Raycast System
    from systems.raycast import RaycastSystem
    ray_sys = RaycastSystem()
    engine.add_system(ray_sys, phase=Phase.INPUT)
    
    # 3. Add GUI System
    from systems.gui import GUIDebugSystem
    gui_sys = GUIDebugSystem()
    engine.add_system(gui_sys, phase=Phase.TELEMETRY)
    
    # 3. Setup Scene
    # Camera
    camera = world.add_entity()
    world.add_component(camera, CameraComponent(fov=60.0, near=0.1, far=100.0))
    world.add_component(camera, TransformComponent(x=0, y=0))
    
    # Blue Rotating Cube
    cube = world.add_entity()
    world.add_component(cube, MeshComponent(mesh_path="cube"))
    world.add_component(cube, MaterialComponent(diffuse_color=[0.0, 0.5, 1.0, 1.0]))
    world.add_component(cube, TransformComponent(x=0, y=0))
    
    # Red Static Cube
    cube2 = world.add_entity()
    world.add_component(cube2, MeshComponent(mesh_path="cube"))
    world.add_component(cube2, MaterialComponent(diffuse_color=[1.0, 0.2, 0.2, 1.0]))
    world.add_component(cube2, TransformComponent(x=2, y=1))
    
    print("Starting Engine...")
    start_time = time.time()
    
    # The engine.run() will block until GUI window is closed
    await engine.run()
    
    print("Verification finished.")

if __name__ == "__main__":
    asyncio.run(main())
