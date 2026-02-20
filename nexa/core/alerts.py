import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from nexa.tools.registry import registry

logger = logging.getLogger(__name__)

class Alert:
    def __init__(self, title: str, message: str, severity: str = "info", category: str = "general"):
        self.title = title
        self.message = message
        self.severity = severity
        self.category = category
        self.timestamp = datetime.now()

class AlertManager:
    """
    Manage system-wide alerts and route them to communication channels
    """
    def __init__(self):
        self.history: List[Alert] = []
        self.handlers = []

    async def emit(self, title: str, message: str, severity: str = "info", category: str = "general"):
        """
        Emit a new alert
        """
        alert = Alert(title, message, severity, category)
        self.history.append(alert)

        logger.info(f"🔔 ALERT [{severity.upper()}]: {title} - {message}")

        # Route to communication tool if severe
        if severity in ['high', 'critical']:
            await self._route_to_comm_channels(alert)

    async def _route_to_comm_channels(self, alert: Alert):
        """
        Automatically route high severity alerts to communication channels
        """
        from nexa.core.engine import engine
        if engine.messaging_hub:
            try:
                msg = f"🔔 [{alert.severity.upper()}] {alert.title}: {alert.message}"
                # Route critical to all, high to Telegram/SMS
                platforms = ["telegram", "sms"] if alert.severity == "high" else ["telegram", "discord", "slack", "sms", "email"]
                await engine.messaging_hub.notify(msg, platforms=platforms)
            except Exception as e:
                logger.error(f"Failed to route alert via hub: {e}")

    async def get_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        return [
            {
                "title": a.title,
                "message": a.message,
                "severity": a.severity,
                "category": a.category,
                "timestamp": a.timestamp.isoformat()
            }
            for a in self.history[-count:]
        ]

# Global alert manager
alert_manager = AlertManager()
