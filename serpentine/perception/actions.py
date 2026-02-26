import logging
import asyncio
import time
from typing import Optional, Dict, Any, List
try:
    import pyautogui
    # Safety feature for PyAutoGUI
    pyautogui.FAILSAFE = True
except ImportError:
    pyautogui = None

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World
from serpentine.perception.components import ActionBufferComponent
from serpentine.mind.intent import Intent, ClickIntent, MoveIntent, KeyIntent

logger = logging.getLogger(__name__)

@Registry.register_system(phase=SystemPhase.EXECUTION, modes=[EngineMode.ARCHITECT, EngineMode.TEACHER, EngineMode.PRODUCTION])
class ActionExecutionSystem(System):
    """
    Executes pending actions (Intents) from the ActionBufferComponent using PyAutoGUI.
    """
    def __init__(self, tick_rate: int = None):
        super().__init__(tick_rate=tick_rate)
        if pyautogui is None:
            logger.warning("PyAutoGUI not installed. ActionExecutionSystem will be disabled.")

    async def update(self, world: World, dt: float) -> None:
        if pyautogui is None:
            return

        entities = world.get_components(ActionBufferComponent)

        for entity_id, buffer in entities.items():
            # Clear previous frame's executed action
            buffer.last_executed_intent = None

            # Process all pending actions or one per tick?
            # Usually one physical action per tick or as many as possible?
            # Let's do one per tick to simulate realistic speed/delay handling if needed.
            # But buffer implies queue. Let's process one.

            action = buffer.dequeue()
            if action:
                self._execute(action)
                buffer.last_executed_intent = action
                buffer.history.append((time.time(), action))
                if len(buffer.history) > 100:
                    buffer.history.pop(0)

    def _execute(self, action: Intent):
        try:
            if action.type == "click":
                # Validate coordinates
                if isinstance(action, ClickIntent):
                    # Check bounds? PyAutoGUI handles screen bounds usually.
                    pyautogui.click(x=action.x, y=action.y, button=getattr(action, 'button', 'left'))
                else:
                    # Fallback for generic dict-like access if not casted
                    x = action.params.get('x')
                    y = action.params.get('y')
                    btn = action.params.get('button', 'left')
                    if x is not None and y is not None:
                        pyautogui.click(x=x, y=y, button=btn)

            elif action.type == "move":
                if isinstance(action, MoveIntent):
                    pyautogui.moveTo(action.x, action.y, duration=action.duration)
                else:
                    x = action.params.get('x')
                    y = action.params.get('y')
                    dur = action.params.get('duration', 0.0)
                    if x is not None and y is not None:
                        pyautogui.moveTo(x, y, duration=dur)

            elif action.type == "key":
                if isinstance(action, KeyIntent):
                    key = action.key
                    act = action.action
                    if act == "press":
                        pyautogui.press(key)
                    elif act == "down":
                        pyautogui.keyDown(key)
                    elif act == "up":
                        pyautogui.keyUp(key)
                else:
                    key = action.params.get('key')
                    act = action.params.get('action', 'press')
                    if key:
                        if act == "press":
                            pyautogui.press(key)
                        elif act == "down":
                            pyautogui.keyDown(key)
                        elif act == "up":
                            pyautogui.keyUp(key)

        except Exception as e:
            logger.error(f"Failed to execute action {action}: {e}")
