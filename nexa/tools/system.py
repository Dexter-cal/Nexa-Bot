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
from typing import Optional, Dict

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
