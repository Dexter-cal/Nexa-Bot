import os
import shutil
from nexa.tools.base import Tool, ToolResult
from typing import Optional, List

class FileReadTool(Tool):
    name = "file.read"
    description = "Read file contents"
    category = "file"
    risk_level = "medium"
    parameters = {
        "path": {"type": "string", "required": True}
    }

    async def execute(self, path: str, **kwargs) -> ToolResult:
        try:
            if not os.path.exists(path):
                return ToolResult(success=False, error=f"File not found: {path}")
            with open(path, 'r') as f:
                content = f.read()
            return ToolResult(success=True, output=content)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class FileWriteTool(Tool):
    name = "file.write"
    description = "Write to a file"
    category = "file"
    risk_level = "high"
    parameters = {
        "path": {"type": "string", "required": True},
        "content": {"type": "string", "required": True}
    }

    async def execute(self, path: str, content: str, **kwargs) -> ToolResult:
        try:
            with open(path, 'w') as f:
                f.write(content)
            return ToolResult(success=True, output=f"File written: {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class FileDeleteTool(Tool):
    name = "file.delete"
    description = "Delete a file"
    category = "file"
    risk_level = "high"
    parameters = {
        "path": {"type": "string", "required": True}
    }

    async def execute(self, path: str, **kwargs) -> ToolResult:
        try:
            if not os.path.exists(path):
                return ToolResult(success=False, error=f"File not found: {path}")
            os.remove(path)
            return ToolResult(success=True, output=f"File deleted: {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
