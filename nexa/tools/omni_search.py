import asyncio
import logging
from typing import Dict, Any, List
from nexa.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class OmniSearchTool(Tool):
    name = "web.omni_search"
    description = "Search across local files, the web, and all connected Nexa peers simultaneously."
    category = "web"
    risk_level = "low"
    parameters = {
        "query": {"type": "string", "required": True},
        "search_depth": {"type": "integer", "required": False, "default": 2}
    }

    async def execute(self, query: str, search_depth: int = 2, **kwargs) -> ToolResult:
        from nexa.core.engine import engine
        from nexa.core.network_node import network_node

        logger.info(f"🔍 Omni-Search: Querying all sources for '{query}'...")

        # 1. Local Memory Search
        local_task = engine.memory.search(query, limit=5)

        # 2. Web Search (Simulated call to WebSearchTool)
        web_task = self._simulated_web_search(query)

        # 3. Peer Search
        await network_node.load_peers()
        peer_task = network_node.broadcast(f"memory search {query}")

        results = await asyncio.gather(local_task, web_task, peer_task, return_exceptions=True)

        combined_results = {
            "local_memory": results[0] if not isinstance(results[0], Exception) else [],
            "web_results": results[1] if not isinstance(results[1], Exception) else [],
            "peer_insights": results[2] if not isinstance(results[2], Exception) else []
        }

        return ToolResult(success=True, output=combined_results)

    async def _simulated_web_search(self, query: str):
        # Mocking the Web Search tool result
        return [
            {"title": f"Web result for {query}", "url": "https://nexa.ai/docs", "snippet": "Found relevant info on the web."}
        ]
