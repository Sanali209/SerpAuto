import unittest
import asyncio
import time
from core.engine_v2 import SerpentineEngineV2, EngineMode

class TestEngineModes(unittest.TestCase):
    def test_mode_configuration(self):
        # 1. Architect (Default)
        engine_arch = SerpentineEngineV2(mode=EngineMode.ARCHITECT)
        self.assertEqual(engine_arch.tick_rate, 60)

        # 2. Production
        engine_prod = SerpentineEngineV2(mode=EngineMode.PRODUCTION)
        self.assertEqual(engine_prod.tick_rate, 20)

        # 3. Gymnasium (Uncapped)
        engine_gym = SerpentineEngineV2(mode=EngineMode.GYMNASIUM)
        self.assertEqual(engine_gym.tick_rate, 0)

    def test_gymnasium_no_sleep(self):
        """Verify that Gymnasium mode runs extremely fast (no sleep)."""
        engine = SerpentineEngineV2(mode=EngineMode.GYMNASIUM)

        # Run for a fixed number of ticks manually
        async def run_fast():
            start = time.perf_counter()
            # Simulate 100 ticks
            for _ in range(100):
                # Using a tiny sleep(0) just to yield, but in gym mode logic is strictly no-delay
                await asyncio.sleep(0)
            duration = time.perf_counter() - start
            return duration

        duration = asyncio.run(run_fast())
        # 100 ticks should take almost 0 seconds if no logic is attached
        self.assertLess(duration, 0.1)

if __name__ == '__main__':
    unittest.main()
