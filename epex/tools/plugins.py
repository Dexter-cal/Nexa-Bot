import logging
import os
import httpx
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class PluginLoaderTool(Tool):
    name = "meta.load_plugin"
    description = "Load an external Epex tool from a provided Python source URL or file."
    category = "meta"
    risk_level = "critical"
    parameters = {
        "source": {"type": "string", "required": True, "description": "URL or local path to the tool's Python code"},
        "plugin_name": {"type": "string", "required": True}
    }

    async def execute(self, source: str, plugin_name: str, **kwargs) -> ToolResult:
        logger.info(f"Loading plugin {plugin_name} from {source}...")

        try:
            if source.startswith("http"):
                async with httpx.AsyncClient() as client:
                    response = await client.get(source)
                    code = response.text
            else:
                if not os.path.exists(source):
                    return ToolResult(success=False, error=f"Source path not found: {source}")
                with open(source, 'r') as f:
                    code = f.read()

            from epex.tools.registry import registry
            new_tool = registry.register_from_code(code)

            return ToolResult(success=True, output=f"Plugin '{plugin_name}' loaded successfully as '{new_tool.name}'.")

        except Exception as e:
            return ToolResult(success=False, error=f"Failed to load plugin: {str(e)}")
