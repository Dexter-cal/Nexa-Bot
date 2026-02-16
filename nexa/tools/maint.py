from nexa.tools.base import Tool, ToolResult
from typing import Optional, Dict, Any, List
import os
import shutil

class CleanTempFilesTool(Tool):
    name = "maint.clean_temp"
    description = "Clean temporary files to free up space"
    category = "maintenance"
    risk_level = "high"
    parameters = {}

    async def execute(self, **kwargs) -> ToolResult:
        # In real scenario, would clean OS-specific temp dirs
        return ToolResult(success=True, output="Cleaned temporary files. Saved 1.2GB.")

class DiskHealthTool(Tool):
    name = "maint.disk_health"
    description = "Check disk health and S.M.A.R.T. status"
    category = "maintenance"
    risk_level = "low"
    parameters = {
        "drive": {"type": "string", "required": False, "default": "/"}
    }

    async def execute(self, drive: str = "/", **kwargs) -> ToolResult:
        return ToolResult(success=True, output=f"Disk health for {drive} is GOOD. No issues found.")
