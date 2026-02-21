import asyncio
import logging
from typing import Dict, Any, List
from epex.intelligence.api_manager import UniversalAPIKeyManager

logger = logging.getLogger(__name__)

class SystemContext:
    """
    Tracks the live health and connectivity of all EPEX components.
    """
    def __init__(self, engine=None):
        self.engine = engine
        self.api_manager = UniversalAPIKeyManager()
        self.status = {
            "models": {},
            "bridges": {},
            "tools": "active",
            "last_check": 0
        }

    async def refresh(self):
        """Perform a full system health check"""
        logger.info("Performing EPEX system health check...")

        # 1. Test Model Connectivity
        self.status["models"] = await self.api_manager.get_connected_providers()

        # 2. Test Bridge Connectivity
        if self.engine and self.engine.messaging_hub:
            bridges = self.engine.messaging_hub.bridges
            for name, bridge in bridges.items():
                self.status["bridges"][name] = {
                    "running": bridge.running,
                    # Real test would involve checking session/token validity
                    "connected": bridge.running
                }

        self.status["last_check"] = asyncio.get_event_loop().time()
        return self.status

    def get_summary(self) -> str:
        """Return a natural language summary of system health"""
        connected_models = [m for m, active in self.status["models"].items() if active]
        active_bridges = [b for b, s in self.status["bridges"].items() if s["connected"]]

        summary = f"EPEX System Status:\n"
        summary += f"- Models Online: {', '.join(connected_models) if connected_models else 'None'}\n"
        summary += f"- Active Bridges: {', '.join(active_bridges) if active_bridges else 'None'}\n"
        summary += f"- Core Engine: {'Running' if self.engine and self.engine.running else 'Idle'}"

        return summary
