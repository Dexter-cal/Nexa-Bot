import os
import importlib.util
import logging
import sys
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class PluginLoaderTool(Tool):
    name = "meta.load_plugins"
    description = "Scan the 'plugins/' directory and dynamically register new tools without restarting the engine."
    category = "meta"
    risk_level = "high"
    parameters = {
        "plugin_path": {"type": "string", "required": False, "default": "plugins/", "description": "Custom directory to scan for plugins."}
    }

    async def execute(self, plugin_path: str = "plugins/", **kwargs) -> ToolResult:
        if not os.path.exists(plugin_path):
            os.makedirs(plugin_path)
            return ToolResult(success=True, output=f"Created plugin directory at {plugin_path}. No plugins found.")

        from epex.tools.registry import registry
        loaded = []
        errors = []

        for filename in os.listdir(plugin_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"plugin_{filename[:-3]}"
                file_path = os.path.join(plugin_path, filename)

                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, Tool) and
                            attr is not Tool):

                            tool_instance = attr()
                            registry.register(tool_instance)
                            loaded.append(tool_instance.name)

                except Exception as e:
                    logger.error(f"Failed to load plugin {filename}: {e}")
                    errors.append(f"{filename}: {str(e)}")

        return ToolResult(success=True, output={
            "message": f"Plugin scan complete. Loaded {len(loaded)} new tools.",
            "loaded_tools": loaded,
            "errors": errors
        })
