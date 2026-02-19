import logging
import asyncio
from typing import Dict, Any, List
from nexa.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class ModelZooExplorerTool(Tool):
    name = "intelligence.model_zoo"
    description = "Explore and list all available AI models across all configured providers."
    category = "intelligence"
    risk_level = "low"
    parameters = {
        "provider": {"type": "string", "required": False, "description": "Filter by specific provider"}
    }

    async def execute(self, provider: str = None, **kwargs) -> ToolResult:
        from nexa.intelligence.api_manager import UniversalAPIKeyManager
        mgr = UniversalAPIKeyManager()
        keys = await mgr.auto_detect_keys()

        available_models = []

        providers_to_check = [provider] if provider else mgr.providers.keys()

        for p in providers_to_check:
            if p in mgr.providers:
                info = mgr.providers[p]
                status = "Connected" if p in keys else "Not Configured"

                models = info.get('models', [])
                if isinstance(models, str):
                    models = [models]

                available_models.append({
                    "provider": info['name'],
                    "status": status,
                    "models": models,
                    "free_tier": info.get('free_tier', False),
                    "cost": info.get('cost', 'Unknown')
                })

        return ToolResult(success=True, output=available_models)
