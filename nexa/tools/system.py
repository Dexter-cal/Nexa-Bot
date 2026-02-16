import psutil
import os
# Mock pyautogui if DISPLAY is not set to avoid import errors in headless environments
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

try:
    import pyautogui
except:
    pyautogui = None
from nexa.tools.base import Tool, ToolResult
from typing import Optional, Dict, List

class SystemInfoTool(Tool):
    name = "system.info"
    description = "Get system information (CPU, memory, disk)"
    category = "system"
    risk_level = "low"
    parameters = {}

    async def execute(self, **kwargs) -> ToolResult:
        try:
            info = {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage('/')._asdict()
            }
            return ToolResult(success=True, output=info)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class ScreenshotTool(Tool):
    name = "system.screenshot"
    description = "Capture a screenshot of the screen"
    category = "system"
    risk_level = "low"
    parameters = {
        "save_path": {"type": "string", "required": False}
    }

    async def execute(self, save_path: Optional[str] = None, **kwargs) -> ToolResult:
        if not pyautogui:
            return ToolResult(success=False, error="pyautogui not available (no display?)")
        try:
            screenshot = pyautogui.screenshot()
            if save_path:
                screenshot.save(save_path)
            return ToolResult(success=True, output="Screenshot captured")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class MouseControlTool(Tool):
    name = "system.mouse"
    description = "Control the mouse cursor"
    category = "system"
    risk_level = "medium"
    parameters = {
        "action": {"type": "string", "required": True}, # click, move, scroll
        "x": {"type": "integer", "required": False},
        "y": {"type": "integer", "required": False},
        "clicks": {"type": "integer", "required": False, "default": 1}
    }

    async def execute(self, action: str, x: int = None, y: int = None, clicks: int = 1, **kwargs) -> ToolResult:
        if not pyautogui: return ToolResult(success=False, error="pyautogui not available")
        try:
            if action == "move":
                pyautogui.moveTo(x, y, duration=0.2)
            elif action == "click":
                pyautogui.click(x, y, clicks=clicks)
            elif action == "scroll":
                pyautogui.scroll(clicks)
            return ToolResult(success=True, output=f"Mouse {action} successful")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class KeyboardControlTool(Tool):
    name = "system.keyboard"
    description = "Control keyboard input"
    category = "system"
    risk_level = "medium"
    parameters = {
        "action": {"type": "string", "required": True}, # type, press, hotkey
        "text": {"type": "string", "required": False},
        "keys": {"type": "list", "required": False}
    }

    async def execute(self, action: str, text: str = None, keys: List[str] = None, **kwargs) -> ToolResult:
        if not pyautogui: return ToolResult(success=False, error="pyautogui not available")
        try:
            if action == "type":
                pyautogui.write(text, interval=0.01)
            elif action == "press":
                pyautogui.press(keys)
            elif action == "hotkey":
                pyautogui.hotkey(*keys)
            return ToolResult(success=True, output=f"Keyboard {action} successful")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

from typing import List
