import asyncio
import time
from typing import List
from .world import World
from .system import System

class SerpentineEngine:
    def __init__(self):
        self.world = World()
        self.systems: List[System] = [] # List of all System (Perception, Brain, Action)
        self.is_running = False
        self.tick_rate = 20 # Limit TPS for Production/Debug

    def add_system(self, system: System):
        self.systems.append(system)

    async def run(self):
        self.is_running = True
        last_time = time.perf_counter()

        while self.is_running:
            current_time = time.perf_counter()
            dt = current_time - last_time
            last_time = current_time

            # 1. Execute all systems sequentially
            for system in self.systems:
                await system.update(self.world, dt)

            # 2. Artificial delay (Sleep)
            # In Gymnasium (RL Gym) mode we ignore sleep for max speed
            elapsed = time.perf_counter() - current_time
            sleep_time = max(0, (1.0 / self.tick_rate) - elapsed)
            await asyncio.sleep(sleep_time)

    def stop(self):
        self.is_running = False
