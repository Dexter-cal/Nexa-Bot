import logging
import os
import json
from typing import Dict, Any, List
from nexa.tools.base import Tool, ToolResult
from nexa.intelligence.router import EnhancedLLMRouter

logger = logging.getLogger(__name__)

class SelfEvolutionTool(Tool):
    name = "meta.self_evolve"
    description = "Analyze a specific Nexa component and propose/apply an upgrade to its logic."
    category = "meta"
    risk_level = "critical"
    parameters = {
        "component_path": {"type": "string", "required": True, "description": "Path to the component to evolve"},
        "objective": {"type": "string", "required": True, "description": "What improvement to achieve (e.g. 'add error handling', 'optimize speed')"}
    }

    async def execute(self, component_path: str, objective: str, **kwargs) -> ToolResult:
        if not os.path.exists(component_path):
            return ToolResult(success=False, error=f"Component not found: {component_path}")

        logger.info(f"🧬 Self-Evolution: Analyzing {component_path} to achieve: {objective}")

        with open(component_path, 'r') as f:
            current_code = f.read()

        router = EnhancedLLMRouter()
        prompt = f"""
        Objective: {objective}
        Component: {component_path}

        Current Code:
        ```python
        {current_code}
        ```

        Rewrite the complete file to achieve the objective while maintaining full compatibility.
        Return ONLY the Python code in a code block.
        """

        response = await router.execute(prompt, priority='quality')
        new_code_raw = response['response']

        # Extract code
        if '```python' in new_code_raw:
            new_code = new_code_raw.split('```python')[1].split('```')[0].strip()
        elif '```' in new_code_raw:
            new_code = new_code_raw.split('```')[1].split('```')[0].strip()
        else:
            new_code = new_code_raw.strip()

        # Apply using meta.update_self (via registry to find the tool)
        from nexa.tools.registry import registry
        updater = registry.get("meta.update_self")
        if not updater:
             return ToolResult(success=False, error="meta.update_self tool not found")

        res = await updater.execute(component_path=component_path, new_code=new_code)

        return ToolResult(success=res.success, output=f"Evolution complete: {res.output}", error=res.error)
