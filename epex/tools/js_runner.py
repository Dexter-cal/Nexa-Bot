"""
Javascript & Node.js Execution Environment for EPEX APEX v5.0
Allows the agent to run JS scripts, manage npm packages, and execute Node-based tools.
"""

import asyncio
import os
import subprocess
import logging
from typing import Dict, Any, List, Optional
from epex.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class NodeJsRunnerTool(Tool):
    name = "js.node_run"
    description = "Run a Node.js script or command."
    category = "javascript"
    risk_level = "high"
    parameters = {
        "code": {"type": "string", "required": False, "description": "Raw Javascript code to execute."},
        "file_path": {"type": "string", "required": False, "description": "Path to an existing .js file."},
        "args": {"type": "list", "required": False, "description": "Command line arguments for the script."}
    }

    async def execute(self, code: str = None, file_path: str = None, args: List[str] = None, **kwargs) -> ToolResult:
        if not code and not file_path:
            return ToolResult(success=False, error="Either 'code' or 'file_path' must be provided.")

        temp_file = None
        if code:
            import tempfile
            with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as tf:
                tf.write(code)
                temp_file = tf.name
            target = temp_file
        else:
            target = file_path

        cmd = ["node", target] + (args or [])

        try:
            logger.info(f"NodeJS: Executing {target}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            success = process.returncode == 0
            return ToolResult(
                success=success,
                output=stdout.decode(),
                error=stderr.decode() if not success else None
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

class NpmManagerTool(Tool):
    name = "js.npm"
    description = "Manage Node.js packages using npm."
    category = "javascript"
    risk_level = "medium"
    parameters = {
        "action": {"type": "string", "required": True}, # install, uninstall, list, update
        "package": {"type": "string", "required": False},
        "path": {"type": "string", "required": False, "default": "."}
    }

    async def execute(self, action: str, package: str = None, path: str = ".", **kwargs) -> ToolResult:
        cmd = ["npm", action]
        if package:
            cmd.append(package)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return ToolResult(success=process.returncode == 0, output=stdout.decode(), error=stderr.decode() if process.returncode != 0 else None)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
