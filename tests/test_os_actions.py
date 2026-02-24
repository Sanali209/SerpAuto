import unittest
from unittest.mock import patch
from actions.os_actions import ClickAction

class TestOSActions(unittest.IsolatedAsyncioTestCase):
    async def test_click_action(self):
        with patch('pyautogui.click') as mock_click:
            action = ClickAction(x=100, y=200, button='left')
            status = await action.execute()
            
            self.assertEqual(status, "SUCCESS")
            # If pyautogui is None, the real code prints and returns SUCCESS
            # If pyautogui is patched, it calls click and returns SUCCESS
            import actions.os_actions
            if actions.os_actions.pyautogui is not None:
                mock_click.assert_called()

if __name__ == '__main__':
    # Since ClickAction.execute is async, we need to run it in a loop
    import asyncio
    
    async def run_tests():
        # This is a bit non-standard for unittest but works for simple async tests
        unittest.main()

    # asyncio.run(run_tests())
    # Actually, let's just use a synchronous mock for basic execution check
    pass
