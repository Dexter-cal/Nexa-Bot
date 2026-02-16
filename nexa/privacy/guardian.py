import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Set, Any

logger = logging.getLogger(__name__)

class PrivacyGuardian:
    """
    24/7 privacy monitoring and protection system
    """

    def __init__(self):
        self.monitored_data = {
            'emails': set(),
            'usernames': set(),
            'passwords': set(), # Hashed
        }
        self.findings = []
        self.monitoring = False

        from nexa.privacy.breach_detector import BreachDetector
        self.breach_detector = BreachDetector()

    async def start_monitoring(self):
        self.monitoring = True
        logger.info("Privacy Guardian activated")

        # Start loops in background
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._breach_check_loop())

    async def _monitoring_loop(self):
        from nexa.privacy.darkweb_monitor import DarkWebMonitor
        monitor = DarkWebMonitor()
        while self.monitoring:
            try:
                # Simulate dark web/paste site monitoring
                logger.debug("Privacy Guardian scanning paste sites...")
                for email in self.monitored_data['emails']:
                     findings = await monitor.search_paste_sites(email)
                     for finding in findings:
                          await self._handle_finding(finding, "darkweb")
                await asyncio.sleep(3600) # Check every hour
            except Exception as e:
                logger.error(f"Error in privacy monitoring: {e}")
                await asyncio.sleep(10)

    async def _breach_check_loop(self):
        from nexa.privacy.digital_scanner import DigitalLifeScanner
        scanner = DigitalLifeScanner()
        while self.monitoring:
            try:
                issues = await scanner.scan_files()
                for issue in issues:
                    await self._handle_finding(issue, "digital_scan")
                await asyncio.sleep(86400) # Check daily
            except Exception as e:
                logger.error(f"Error in breach check loop: {e}")
                await asyncio.sleep(60)

    async def _handle_finding(self, finding: Dict, source: str):
        self.findings.append({
            'finding': finding,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
        logger.warning(f"Privacy Alert from {source}: {finding}")

    async def add_monitored_data(self, data_type: str, value: str):
        if data_type in self.monitored_data:
            if data_type == 'passwords':
                value = hashlib.sha256(value.encode()).hexdigest()
            self.monitored_data[data_type].add(value)
            logger.info(f"Added {data_type} to privacy monitoring")

    async def get_summary(self) -> Dict[str, Any]:
        return {
            'monitored_items': {k: len(v) for k, v in self.monitored_data.items()},
            'total_findings': len(self.findings),
            'status': "active" if self.monitoring else "inactive"
        }
