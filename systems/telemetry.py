from core.system import System
from core.world import World

class TelemetrySystem(System):
    """
    Logs engine metrics (FPS, Entity Count) to stdout or external service.
    Active in PRODUCTION mode.
    """
    async def update(self, world: World, dt: float):
        # Placeholder: Print stats every 60 ticks or so
        # print(f"[Telemetry] DT: {dt:.4f}s")
        pass
