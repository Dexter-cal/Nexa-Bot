import asyncio
import pyautogui
from typing import Dict, List

class PlaybackEngine:
    """
    Play back recorded workflows
    """
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

    async def play(self, workflow: Dict, speed: float = 1.0):
        print(f"▶️  Playing workflow: {workflow.get('name', 'unnamed')}")
        for step in workflow.get('steps', []):
            await self._execute_step(step, speed)

    async def _execute_step(self, step: Dict, speed: float):
        action = step.get('action')
        if action == 'click':
            pyautogui.moveTo(step['x'], step['y'], duration=0.5/speed)
            pyautogui.click()
        elif action == 'type':
            text = "".join(step.get('keys', []))
            pyautogui.write(text, interval=0.05/speed)
        await asyncio.sleep(0.5 / speed)
