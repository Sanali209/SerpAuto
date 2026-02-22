from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase

@register_system(phase=Phase.TELEMETRY)
class TelemetrySystem(System):
    """
    Logs engine metrics (FPS, Entity Count) to stdout or external service.
    Active in PRODUCTION mode.
    """
    async def update(self, world: World, dt: float):
        # Placeholder: Print stats every 60 ticks or so
        # print(f"[Telemetry] DT: {dt:.4f}s")
        pass
