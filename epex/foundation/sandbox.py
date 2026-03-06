import importlib.util
import os
import sys
import tempfile
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from epex.tools.base import Tool, ToolResult

class Sandbox:
    """
    A basic sandbox for executing and testing code in isolation.
    """
    def __init__(self, restricted=True):
        self.restricted = restricted
        self.temp_dir = tempfile.mkdtemp(prefix="epex_sandbox_")

    def __del__(self):
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    async def run_tool(self, code: str, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        """
        Executes a tool from code string within the sandbox.
        """
        module_name = f"sandbox_tool_{uuid.uuid4().hex}"
        temp_file_path = os.path.join(self.temp_dir, f"{module_name}.py")

        try:
            with open(temp_file_path, 'w') as f:
                f.write(code)

            # Use importlib to load the code
            spec = importlib.util.spec_from_file_location(module_name, temp_file_path)
            module = importlib.util.module_from_spec(spec)

            # Simple restricted environment (can be much more complex)
            if self.restricted:
                # Add basic safety by limiting globals?
                # Very difficult in pure Python.
                pass

            spec.loader.exec_module(module)

            # Find the Tool class
            tool_class = None
            for attr in dir(module):
                val = getattr(module, attr)
                if isinstance(val, type) and issubclass(val, Tool) and val is not Tool:
                    if hasattr(val, 'name') and val.name == tool_name:
                        tool_class = val
                        break
                    elif not tool_name:
                        tool_class = val
                        break

            if not tool_class:
                return ToolResult(success=False, error=f"Tool '{tool_name}' not found in code.")

            instance = tool_class()
            return await instance.execute(**params)

        except Exception as e:
            return ToolResult(success=False, error=str(e))
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def cleanup(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
