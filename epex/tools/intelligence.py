import logging
from typing import Any
from epex.tools.base import Tool, ToolResult
from epex.intelligence.neuro_link import NeuroLinkCore

logger = logging.getLogger(__name__)

class NeuroLinkTool(Tool):
    name = "intelligence.neuro_link"
    description = "Analyze recent environment signals and provide proactive tool recommendations."
    category = "intelligence"
    risk_level = "low"
    parameters = {
        "signal": {"type": "string", "required": True}
    }

    async def execute(self, signal: str, **kwargs) -> ToolResult:
        core = NeuroLinkCore()
        results = await core.process_signal(signal)
        return ToolResult(success=True, output={
            "signal_processed": signal,
            "suggestions": results,
            "count": len(results)
        })
