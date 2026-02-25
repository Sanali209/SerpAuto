import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import json
import asyncio

# Mock dearpygui before importing systems that use it
# We need to ensure dpg is mocked globally for this process
mock_dpg = MagicMock()
sys.modules['dearpygui.dearpygui'] = mock_dpg
sys.modules['dearpygui'] = MagicMock()
sys.modules['dearpygui'].dearpygui = mock_dpg

# Constants that might be used
mock_dpg.mvKey_W = 87
mock_dpg.mvKey_S = 83
mock_dpg.mvKey_A = 65
mock_dpg.mvKey_D = 68
mock_dpg.mvKey_Up = 38
mock_dpg.mvKey_Down = 40
mock_dpg.mvKey_Left = 37
mock_dpg.mvKey_Right = 39

from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.core.world import World
from serpentine.components.simulation import RewardComponent, GoalComponent, DatasetConfigComponent, InputControlComponent
from serpentine.perception.components import ActionBufferComponent
from serpentine.mind.intent import KeyIntent
from serpentine.systems.input import HumanInputSystem
from serpentine.systems.data import DatasetLoggerSystem, EnvironmentJudgeSystem
from serpentine.perception.actions import ActionExecutionSystem
from serpentine.components.standard import TransformComponent

class TestSimulation(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Backup Registry
        self.original_components = Registry._components.copy()
        self.original_systems = Registry._systems.copy()
        self.world = World()

    def tearDown(self):
        # Restore Registry
        Registry._components = self.original_components
        Registry._systems = self.original_systems

    async def test_reward_component(self):
        entity = self.world.create_entity()
        reward = RewardComponent()
        self.world.add_component(entity, reward)

        system = EnvironmentJudgeSystem()
        await system.update(self.world, 0.1)

        self.assertAlmostEqual(reward.current_reward, 0.1)
        self.assertAlmostEqual(reward.cumulative_reward, 0.1)

        await system.update(self.world, 0.1)
        self.assertAlmostEqual(reward.cumulative_reward, 0.2)

    async def test_human_input_system(self):
        entity = self.world.create_entity()
        input_comp = InputControlComponent()
        action_buffer = ActionBufferComponent()
        self.world.add_component(entity, input_comp)
        self.world.add_component(entity, action_buffer)

        system = HumanInputSystem()
        # Initialize key map manually because dpg constants are mocked
        system.key_map = {
            mock_dpg.mvKey_W: "Up"
        }

        # Mock dpg behavior
        mock_dpg.is_dearpygui_running.return_value = True

        # Scenario 1: Key pressed
        mock_dpg.is_key_down.side_effect = lambda k: k == mock_dpg.mvKey_W

        await system.update(self.world, 0.1)

        self.assertEqual(len(action_buffer.action_queue), 1)
        intent = action_buffer.action_queue[0]
        self.assertIsInstance(intent, KeyIntent)
        self.assertEqual(intent.key, "Up")

        # Clear queue
        action_buffer.clear()

        # Scenario 2: No key pressed
        mock_dpg.is_key_down.side_effect = lambda k: False
        await system.update(self.world, 0.1)
        self.assertEqual(len(action_buffer.action_queue), 0)

    @patch("builtins.open", new_callable=mock_open)
    async def test_dataset_logger_stateful(self, mock_file):
        entity = self.world.create_entity()
        config = DatasetConfigComponent(is_recording=True, dataset_path="test.jsonl")
        transform = TransformComponent(x=10.0, y=20.0)
        action_buffer = ActionBufferComponent()

        self.world.add_component(entity, config)
        self.world.add_component(entity, transform)
        self.world.add_component(entity, action_buffer)

        system = DatasetLoggerSystem()

        # First update: Open file
        await system.update(self.world, 0.1)
        mock_file.assert_called_with("test.jsonl", "a")

        # Second update: Should reuse handle
        mock_file.reset_mock()
        await system.update(self.world, 0.1)
        mock_file.assert_not_called() # Should not call open again

        # Check writing
        # Note: reset_mock() on mock_file (open) also resets the returned handle's history
        # So we expect 1 call since reset
        handle = system.file_handles["test.jsonl"]
        self.assertEqual(handle.write.call_count, 1)

        # Stop recording
        config.is_recording = False
        await system.update(self.world, 0.1)

        # Verify handle closed
        self.assertTrue(handle.close.called)
        self.assertNotIn("test.jsonl", system.file_handles)

    async def test_action_execution_system_clears_intent(self):
        # Mock pyautogui to allow system to run
        with patch("serpentine.perception.actions.pyautogui", new=MagicMock()):
            entity = self.world.create_entity()
            action_buffer = ActionBufferComponent()
            # Set stale intent
            stale_intent = KeyIntent(key="Down")
            action_buffer.last_executed_intent = stale_intent

            self.world.add_component(entity, action_buffer)

            system = ActionExecutionSystem()

            # Update without new actions
            await system.update(self.world, 0.1)

            # Verify last_executed_intent is cleared
            self.assertIsNone(action_buffer.last_executed_intent)

            # Now enqueue action
            new_intent = KeyIntent(key="Up")
            action_buffer.enqueue(new_intent)

            # Mock execute to avoid actual pyautogui call
            # We need to ensure _execute is mocked on the instance or class
            with patch.object(system, '_execute', return_value=None) as mock_exec:
                await system.update(self.world, 0.1)
                mock_exec.assert_called_once()

            # Verify intent is set
            self.assertEqual(action_buffer.last_executed_intent, new_intent)
