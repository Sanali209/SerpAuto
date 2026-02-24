from core.system import System
from core.world import World
from core.registry import register_system
from core.engine_v2 import Phase
from components.spatial import TransformComponent
from components.internal import VelocityComponent, ColliderComponent, RewardComponent

@register_system(phase=Phase.INTERNAL_PHYSICS)
class InternalPhysicsSystem(System):
    """
    Simulates simple physics for internal entities (Position += Velocity * dt).
    """
    async def update(self, world: World, dt: float):
        entities = world.get_entities_with(TransformComponent, VelocityComponent)
        for entity in entities:
            transform = world.get_component(entity, TransformComponent)
            velocity = world.get_component(entity, VelocityComponent)

            # Simple Euler integration
            transform.x += velocity.vx * dt
            transform.y += velocity.vy * dt

            # Placeholder for collision check (ColliderComponent)
            # if world.has_component(entity, ColliderComponent): ...

@register_system(phase=Phase.COGNITION)
class DatasetLoggerSystem(System):
    """
    Logs Perception + Action pairs for Imitation Learning (Teacher Mode).
    Implements On-Action recording and a Ring Buffer to prevent Distributional Shift.
    """
    _instance = None

    def __init__(self, output_dir: str = "dataset_logs"):
        import os
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.record_count = 0
        self.is_recording = False
        self.episode_buffer = []  # Ring buffer
        self.max_buffer_size = 50 # Flush every 50 records to disk
        DatasetLoggerSystem._instance = self

    @classmethod
    def get_instance(cls) -> 'DatasetLoggerSystem':
        return cls._instance

    def toggle_recording(self) -> bool:
        self.is_recording = not self.is_recording
        if not self.is_recording:
            self.flush_to_disk() # Save any remaining data when stopping
        return self.is_recording

    def drop_last_step(self) -> bool:
        """Removes the last recorded action to prevent bad data (Distributional Shift)."""
        if self.episode_buffer:
            self.episode_buffer.pop()
            return True
        return False

    def flush_to_disk(self):
        if not self.episode_buffer:
            return
            
        import json, os
        log_path = os.path.join(self.output_dir, "teacher_log.jsonl")
        with open(log_path, "a", encoding="utf-8") as f:
            for entry in self.episode_buffer:
                f.write(json.dumps(entry) + "\n")
        
        self.record_count += len(self.episode_buffer)
        self.episode_buffer.clear()

    async def update(self, world: World, dt: float):
        if not self.is_recording:
            return
            
        import json
        import os
        from components.core import PerceptionComponent, ActionBufferComponent

        entities = world.get_entities_with(PerceptionComponent, ActionBufferComponent)
        
        for entity in entities:
            perception = world.get_component(entity, PerceptionComponent)
            action_buffer = world.get_component(entity, ActionBufferComponent)

            # We log state transitions if there's an action being taken AND we haven't logged it yet.
            # To avoid double-logging the same action across multiple ticks, we hook into the queue.
            # A simple implementation is tracking the id() of the action or clearing a flag.
            if action_buffer.queue:
                action = action_buffer.queue[0]
                
                # Check if we already recorded this exact action instance
                if getattr(action, "_is_recorded", False):
                    continue
                
                setattr(action, "_is_recorded", True)
                
                log_entry = {
                    "tick": self.record_count + len(self.episode_buffer),
                    "entity": str(entity),
                    "perception": perception.raw_context,
                    "action_type": action.__class__.__name__,
                    "action_params": action.model_dump() if hasattr(action, "model_dump") else str(action)
                }

                self.episode_buffer.append(log_entry)
                
                if len(self.episode_buffer) >= self.max_buffer_size:
                    self.flush_to_disk()

@register_system(phase=Phase.INPUT)
class HumanInputSystem(System):
    """
    Bridge between DearPyGui window clicks and ActionBufferComponent for Teacher Mode.
    """
    async def update(self, world: World, dt: float):
        # Stub: will translate GUI clicks to ClickActions
        pass
