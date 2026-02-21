import psutil
import os
# Mock pyautogui if DISPLAY is not set to avoid import errors in headless environments
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

try:
    import pyautogui
except:
    pyautogui = None
from epex.tools.base import Tool, ToolResult
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

class ProcessListTool(Tool):
    name = "system.process_list"
    description = "Get list of running processes"
    category = "system"
    risk_level = "medium"
    parameters = {}

    async def execute(self, **kwargs) -> ToolResult:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            processes.append(proc.info)
        return ToolResult(success=True, output=processes[:20])

class NetworkStatsTool(Tool):
    name = "system.network_stats"
    description = "Get network interface statistics"
    category = "system"
    risk_level = "low"
    parameters = {}

    async def execute(self, **kwargs) -> ToolResult:
        stats = psutil.net_io_counters(pernic=True)
        return ToolResult(success=True, output={k: v._asdict() for k, v in stats.items()})

class TerminalTool(Tool):
    name = "system.run_command"
    description = "Run a command in the terminal"
    category = "system"
    risk_level = "high"
    parameters = {
        "command": {"type": "string", "required": True}
    }

    async def execute(self, command: str, **kwargs) -> ToolResult:
        import asyncio
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return ToolResult(
                success=process.returncode == 0,
                output=stdout.decode(),
                error=stderr.decode() if process.returncode != 0 else None
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class VisionAnalyzeTool(Tool):
    name = "system.vision_analyze"
    description = "Use AI to analyze the current screen content"
    category = "system"
    risk_level = "low"
    parameters = {
        "prompt": {"type": "string", "required": True}
    }

    async def execute(self, prompt: str, **kwargs) -> ToolResult:
        if not pyautogui: return ToolResult(success=False, error="pyautogui not available")
        try:
            # Capture screen
            screenshot = pyautogui.screenshot()
            # In a real scenario, send this to a Vision model (GPT-4o, Gemini 1.5 Pro)
            # For now, we simulate the analysis
            return ToolResult(success=True, output=f"Vision analysis for '{prompt}': Elements detected on screen.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class SelectCaptureTool(Tool):
    name = "system.select_capture"
    description = "Interactively select a region of the screen and capture it for analysis."
    category = "system"
    risk_level = "medium"
    parameters = {
        "region": {"type": "object", "required": False, "description": "JSON with x, y, width, height. If not provided, it will prompt for manual selection (GUI only)."}
    }

    async def execute(self, region: Optional[Dict[str, int]] = None, **kwargs) -> ToolResult:
        if not pyautogui: return ToolResult(success=False, error="pyautogui not available")
        try:
            if region:
                screenshot = pyautogui.screenshot(region=(region['x'], region['y'], region['width'], region['height']))
            else:
                # This would normally use a GUI overlay for selection
                # For now, we simulate a region
                screenshot = pyautogui.screenshot(region=(0, 0, 500, 500))

            # Save to temporary path for analysis
            temp_path = "epex_selection.png"
            screenshot.save(temp_path)

            return ToolResult(success=True, output={
                "message": "Region captured successfully",
                "path": temp_path,
                "region": region or {"x":0, "y":0, "width":500, "height":500}
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
