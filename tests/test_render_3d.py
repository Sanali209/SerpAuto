import asyncio
import glm
import time
from core.engine_v2 import SerpentineEngineV2, EngineMode, Phase
from components.core import MeshComponent, MaterialComponent, CameraComponent
from components.spatial import TransformComponent

async def main():
    print("Initializing 3D Render Verification...")
    engine = SerpentineEngineV2(mode=EngineMode.PLAY)
    world = engine.world
    
    # 1. Create Camera
    camera = world.add_entity()
    world.add_component(camera, CameraComponent(fov=60.0, near=0.1, far=100.0))
    world.add_component(camera, TransformComponent(x=0, y=0)) # x,y in 2D, but renderer assumes z=10
    
    # 2. Create Rotating Cube
    cube = world.add_entity()
    world.add_component(cube, MeshComponent(mesh_path="cube"))
    world.add_component(cube, MaterialComponent(diffuse_color=[0.0, 0.7, 1.0, 1.0]))
    world.add_component(cube, TransformComponent(x=0, y=0))
    
    print("Starting Engine Update Loop...")
    start_time = time.time()
    
    # Run for a few seconds to verify rendering
    for i in range(100):
        t = time.time() - start_time
        
        # Update cube rotation (simulated via transform update)
        # Note: We don't have a rotation field in TransformComponent yet, 
        # but let's just move it slightly to prove MVP updates.
        transform = world.get_component(cube, TransformComponent)
        transform.x = glm.sin(t) * 2.0
        
        await engine.update_once(0.016) # ~60fps
        # await asyncio.sleep(0.016)
        
    print("Verification loop finished.")

if __name__ == "__main__":
    asyncio.run(main())
