import logging
import asyncio
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult
from epex.tools.registry import registry

logger = logging.getLogger(__name__)

class ApexOptimizerTool(Tool):
    name = "meta.apex_optimize"
    description = "Orchestrate an exhaustive system optimization sequence: health checks, cache clearing, and security hardening."
    category = "meta"
    risk_level = "high"
    parameters = {
        "deep_scan": {"type": "boolean", "required": False, "default": False}
    }

    async def execute(self, deep_scan: bool = False, **kwargs) -> ToolResult:
        logger.info("🚀 APEX OPTIMIZER: Initializing full-stack system optimization...")

        steps = [
            ("maint.optimize", {}),
            ("maint.disk_health", {}),
            ("security.hardening", {}),
            ("system.process_list", {})
        ]

        if deep_scan:
            steps.insert(0, ("maint.deep_scrub", {}))

        results = []
        for tool_name, params in steps:
            tool = registry.get(tool_name)
            if tool:
                logger.info(f"  > Running {tool_name}...")
                res = await tool.execute(**params)
                results.append({"tool": tool_name, "success": res.success})
            else:
                results.append({"tool": tool_name, "success": False, "error": "Tool not found"})

        summary = f"Optimization complete. {sum(1 for r in results if r['success'])}/{len(steps)} systems improved."
        return ToolResult(success=all(r['success'] for r in results), output={"summary": summary, "details": results})
