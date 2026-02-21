import asyncio
import logging
import os
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class SignalMonitorTool(Tool):
    name = "meta.signal_monitor"
    description = "Monitor a file, directory, or webhook for a specific trigger signal."
    category = "meta"
    risk_level = "medium"
    parameters = {
        "target": {"type": "string", "required": True, "description": "Path to file or directory to monitor"},
        "trigger": {"type": "string", "required": True, "description": "The string or event to look for"},
        "action": {"type": "string", "required": True, "description": "The command to run when trigger is detected"},
        "timeout": {"type": "integer", "required": False, "default": 3600}
    }

    async def execute(self, target: str, trigger: str, action: str, timeout: int = 3600, **kwargs) -> ToolResult:
        logger.info(f"Signal Monitor started: Watching {target} for '{trigger}'...")

        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            if os.path.exists(target):
                if os.path.isfile(target):
                    with open(target, 'r') as f:
                        content = f.read()
                        if trigger in content:
                            logger.info(f"SIGNAL DETECTED: {trigger} found in {target}. Executing action...")
                            from epex.core.engine import engine
                            asyncio.create_task(engine.execute_command(action))
                            return ToolResult(success=True, output=f"Trigger detected and action '{action}' initiated.")
                elif os.path.isdir(target):
                    files = os.listdir(target)
                    if trigger in files:
                         logger.info(f"SIGNAL DETECTED: {trigger} file created in {target}. Executing action...")
                         from epex.core.engine import engine
                         asyncio.create_task(engine.execute_command(action))
                         return ToolResult(success=True, output=f"Trigger detected and action '{action}' initiated.")

            await asyncio.sleep(10) # Poll every 10 seconds

        return ToolResult(success=False, error="Signal monitor timed out without detection.")
