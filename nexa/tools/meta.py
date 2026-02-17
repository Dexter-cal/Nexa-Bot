import json
import logging
import importlib
import sys
import os
import asyncio
from typing import List, Dict, Any, Optional
from nexa.tools.base import Tool, ToolResult
from nexa.intelligence.router import EnhancedLLMRouter
from nexa.features.mirror_world import MirrorWorldSandbox

logger = logging.getLogger(__name__)

class ToolGeneratorTool(Tool):
    name = "meta.generate_tool"
    description = "Generate Python code for a new Nexa Bot tool based on a specification"
    category = "meta"
    risk_level = "critical"
    parameters = {
        "spec": {"type": "object", "required": True, "description": "JSON specification of the tool (name, description, parameters, etc.)"}
    }

    def __init__(self, llm_router=None):
        self.llm = llm_router or EnhancedLLMRouter()

    async def execute(self, spec: Dict[str, Any], **kwargs) -> ToolResult:
        prompt = f"""
        Generate Python code for a new Nexa Bot tool with these specifications:

        {json.dumps(spec, indent=2)}

        The tool must:
        1. Inherit from the Tool base class: `from nexa.tools.base import Tool, ToolResult`
        2. Implement the `async def execute(self, **kwargs) -> ToolResult` method.
        3. Define `name`, `description`, `category`, `risk_level`, and `parameters`.
        4. Handle errors gracefully and return a `ToolResult` object.
        5. Be production-ready and follow best practices.

        Return ONLY the Python code, wrapped in a markdown code block.
        """

        try:
            response = await self.llm.execute(prompt, priority='quality')
            content = response['response']

            # Extract code from markdown block
            if '```python' in content:
                code = content.split('```python')[1].split('```')[0].strip()
            elif '```' in content:
                code = content.split('```')[1].split('```')[0].strip()
            else:
                code = content.strip()

            return ToolResult(success=True, output=code)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class ToolTesterTool(Tool):
    name = "meta.test_tool"
    description = "Test a tool's code with provided test cases in a temporary environment"
    category = "meta"
    risk_level = "high"
    parameters = {
        "code": {"type": "string", "required": True, "description": "The Python code of the tool to test"},
        "test_cases": {"type": "list", "required": True, "description": "List of input dicts to test the tool with"}
    }

    async def execute(self, code: str, test_cases: List[Dict[str, Any]], **kwargs) -> ToolResult:
        from nexa.foundation.sandbox import Sandbox

        results = []
        sandbox = Sandbox()

        try:
            for i, test_case in enumerate(test_cases):
                result = await sandbox.run_tool(code, None, test_case)
                results.append({
                    "case": i,
                    "input": test_case,
                    "success": result.success,
                    "output": result.output,
                    "error": result.error
                })

            return ToolResult(success=True, output=results)

        except Exception as e:
            return ToolResult(success=False, error=f"Failed to test tool: {str(e)}")
        finally:
            sandbox.cleanup()

class SelfUpdaterTool(Tool):
    name = "meta.update_self"
    description = "Update its own source code for a specific component"
    category = "meta"
    risk_level = "critical"
    parameters = {
        "component_path": {"type": "string", "required": True, "description": "Relative path to the python file to update"},
        "new_code": {"type": "string", "required": True, "description": "The complete new content of the file"},
        "reload": {"type": "boolean", "required": False, "default": True, "description": "Whether to attempt to reload the component after update"}
    }

    async def execute(self, component_path: str, new_code: str, reload: bool = True, **kwargs) -> ToolResult:
        # Safety check: only allow updating files within the nexa/ directory
        if not component_path.startswith("nexa/") or ".." in component_path:
            return ToolResult(success=False, error="Unauthorized component path. Can only update files within nexa/ directory.")

        if not os.path.exists(component_path):
            return ToolResult(success=False, error=f"Component file not found: {component_path}")

        try:
            # Create a backup
            backup_path = f"{component_path}.bak"
            with open(component_path, 'r') as f:
                old_code = f.read()
            with open(backup_path, 'w') as f:
                f.write(old_code)

            # Write new code
            with open(component_path, 'w') as f:
                f.write(new_code)

            status = f"Successfully updated {component_path}. Backup created at {backup_path}."

            if reload:
                # Attempt to reload. This is experimental.
                # Convert path to module name
                mod_name = component_path.replace("/", ".").replace(".py", "")
                if mod_name in sys.modules:
                    importlib.reload(sys.modules[mod_name])
                    status += f" Component {mod_name} reloaded."

            return ToolResult(success=True, output=status)
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to update component: {str(e)}")

class MirrorWorldSimulateTool(Tool):
    name = "meta.mirror_world_simulate"
    description = "Simulate a task in Mirror-World to predict outcomes"
    category = "meta"
    risk_level = "low"
    parameters = {
        "task": {"type": "string", "required": True},
        "plan": {"type": "list", "required": True}
    }

    async def execute(self, task: str, plan: List[Dict[str, Any]], **kwargs) -> ToolResult:
        sandbox = MirrorWorldSandbox()
        result = await sandbox.simulate_task(task, plan)
        return ToolResult(success=True, output=result)
