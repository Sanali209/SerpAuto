from fastapi import FastAPI
import uvicorn
import asyncio
from threading import Thread
from typing import Optional

from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase

app = FastAPI(title="Serpentine API", description="External Controller for Serpentine Engine")

# Global reference to world for API routes to access
_global_world: Optional[World] = None

@app.get("/metrics")
def get_metrics():
    if not _global_world:
        return {"status": "engine_offline"}
    return {
        "status": "online",
        "total_entities": len(_global_world._entities)
    }

@app.get("/agents")
def get_agents():
    # Placeholder for fetching AgentMetaComponent data
    return {"agents": []}

def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

@register_system(phase=Phase.TELEMETRY)
class FastAPISystem(System):
    """
    Runs a FastAPI server in a background thread to expose engine metrics and controls.
    Mostly used for PRODUCTION / HEADLESS mode.
    """
    def __init__(self):
        self.server_thread = None

    async def update(self, world: World, dt: float):
        global _global_world
        _global_world = world
        
        if self.server_thread is None:
            self.server_thread = Thread(target=run_uvicorn, daemon=True)
            self.server_thread.start()
            print("FastAPI server started on port 8000 (Daemon Thread)")
