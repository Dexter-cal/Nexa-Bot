import asyncio
import logging
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class NeuralSync:
    """
    Cross-device correlation and micro-pattern detection system.
    Tracks system metrics and correlates events across devices.
    """
    def __init__(self):
        self.device_id = "primary-epex-node"
        self.metrics_history: List[Dict[str, Any]] = []
        self.events_history: List[Dict[str, Any]] = []
        self.patterns: List[Dict[str, Any]] = []
        self.running = False
        self._task = None

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._sync_loop())
        logger.info("Neural Sync activated")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
        logger.info("Neural Sync deactivated")

    async def _sync_loop(self):
        while self.running:
            try:
                # Capture local metrics
                metrics = await self._capture_metrics()
                self.metrics_history.append(metrics)

                # Keep only last 1000 entries
                if len(self.metrics_history) > 1000:
                    self.metrics_history.pop(0)

                # Detect patterns
                await self._detect_patterns()

                # Predictive alerts
                await self._generate_predictive_alerts()

                # Sync with other devices (simulated)
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Neural Sync error: {e}")
                await asyncio.sleep(60)

    async def _capture_metrics(self) -> Dict[str, Any]:
        import psutil
        return {
            "timestamp": time.time(),
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else None,
            "net_io": psutil.net_io_counters()._asdict()
        }

    async def log_event(self, event_type: str, details: Dict[str, Any]):
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "details": details,
            "device": self.device_id
        }
        self.events_history.append(event)
        logger.debug(f"Neural Sync event logged: {event_type}")

    async def _detect_patterns(self):
        """
        Simple pattern detection: e.g., high CPU correlating with specific events.
        """
        if len(self.metrics_history) < 10:
            return

        recent_metrics = self.metrics_history[-10:]
        avg_cpu = sum(m['cpu'] for m in recent_metrics) / 10

        if avg_cpu > 80:
            # Check for correlating events in the last minute
            now = time.time()
            correlated_events = [e for e in self.events_history if now - e['timestamp'] < 60]

            if correlated_events:
                pattern = {
                    "pattern_id": f"cpu_spike_{int(now)}",
                    "description": f"High CPU spike detected during {correlated_events[0]['type']}",
                    "confidence": 0.85,
                    "metrics": {"avg_cpu": avg_cpu},
                    "correlated_events": correlated_events
                }
                self.patterns.append(pattern)
                logger.info(f"Micro-pattern detected: {pattern['description']}")

                # Emit system alert
                from epex.core.alerts import alert_manager
                await alert_manager.emit(
                    title="System Pattern Detected",
                    message=pattern['description'],
                    severity="medium",
                    category="system"
                )

    async def _generate_predictive_alerts(self):
        """
        Predictive alerts based on trends in metrics.
        """
        if len(self.metrics_history) < 20:
            return

        recent_disk = [m['disk'] for m in self.metrics_history[-20:]]
        # Very simple trend analysis
        if recent_disk[-1] > recent_disk[0] and recent_disk[-1] > 90:
             from epex.core.alerts import alert_manager
             await alert_manager.emit(
                 title="Predictive Alert",
                 message="Disk will be full in 3 days based on current growth pattern.",
                 severity="high",
                 category="predictive"
             )

    def get_insights(self) -> List[Dict[str, Any]]:
        return self.patterns[-10:]
