from typing import Optional, Dict, Any
import asyncio
import logging
from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World

try:
    from fastapi import FastAPI
    import uvicorn
    from threading import Thread
except ImportError:
    FastAPI = None
    uvicorn = None

logger = logging.getLogger(__name__)

# Global state for bridge
# Using a singleton-like pattern since FastAPI instance is global
_latest_snapshot: Dict[str, Any] = {}

def create_app() -> Optional["FastAPI"]:
    if not FastAPI:
        return None

    app = FastAPI(title="Serpentine Engine Bridge")

    @app.get("/state")
    async def get_state():
        return _latest_snapshot

    return app

@Registry.register_system(phase=SystemPhase.TELEMETRY, modes=[EngineMode.PRODUCTION])
class BridgeSystem(System):
    """
    Exposes engine state via a FastAPI server.
    Configure via World.config['bridge']:
        port: int (default 8000)
        host: str (default "0.0.0.0")
        enabled: bool (default True)
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)
        self.server_thread = None
        self.app = create_app()
        self.started = False

    async def update(self, world: World, dt: float) -> None:
        if not self.app:
            return

        config = world.config.get("bridge", {})
        if not config.get("enabled", True):
            return

        # Update snapshot
        global _latest_snapshot
        _latest_snapshot = world.take_snapshot()

        # Start server if needed
        if not self.started:
            host = config.get("host", "0.0.0.0")
            port = config.get("port", 8000)
            self._start_server(host, port)
            self.started = True

    def _start_server(self, host: str, port: int):
        if not uvicorn:
            logger.warning("Uvicorn not installed, cannot start Bridge server.")
            return

        def run():
            # Disable access log to reduce noise
            uvicorn.run(self.app, host=host, port=port, log_level="warning")

        self.server_thread = Thread(target=run, daemon=True)
        self.server_thread.start()
        logger.info(f"Bridge server started on {host}:{port}")
