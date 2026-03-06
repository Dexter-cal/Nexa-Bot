import time
import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Set, Any
import re

logger = logging.getLogger(__name__)

class PrivacyGuardian:
    """
    24/7 privacy monitoring and protection system
    """

    def __init__(self):
        # User data to monitor
        self.monitored_data = {
            'emails': set(),
            'phone_numbers': set(),
            'usernames': set(),
            'passwords': set(),  # Hashed only
            'api_keys': set(),
            'credit_cards': set(),  # Last 4 digits only
            'addresses': set(),
            'names': set()
        }

        self.findings = []
        self.active_leaks = []
        self.monitoring = False
        self._tasks = []

        from epex.privacy.darkweb_monitor import DarkWebMonitor
        from epex.privacy.breach_detector import BreachDetector
        from epex.privacy.digital_scanner import DigitalLifeScanner
        from epex.privacy.auto_response import AutoResponseSystem

        self.darkweb_monitor = DarkWebMonitor()
        self.breach_detector = BreachDetector()
        self.digital_scanner = DigitalLifeScanner()
        self.auto_responder = AutoResponseSystem()

    async def start_monitoring(self):
        """
        Start 24/7 privacy monitoring
        """
        if self.monitoring:
            return

        self.monitoring = True
        logger.info("🛡️ Privacy Guardian activated")

        # Start monitoring loops
        self._tasks.append(asyncio.create_task(self._darkweb_monitoring_loop()))
        self._tasks.append(asyncio.create_task(self._breach_monitoring_loop()))
        self._tasks.append(asyncio.create_task(self._digital_life_monitoring_loop()))

    async def _darkweb_monitoring_loop(self):
        """
        Continuous dark web monitoring
        """
        while self.monitoring:
            try:
                # Search dark web for user data
                findings = await self.darkweb_monitor.search_all(self.monitored_data)

                # Process findings
                for finding in findings:
                    await self._handle_finding(finding, source='darkweb')

                # Check every 6 hours
                await asyncio.sleep(6 * 3600)
            except Exception as e:
                logger.error(f"Error in dark web monitoring: {e}")
                await asyncio.sleep(60)

    async def _breach_monitoring_loop(self):
        """
        Continuous breach monitoring
        """
        while self.monitoring:
            try:
                # Check for new breaches
                breaches = await self.breach_detector.check_breaches(self.monitored_data['emails'])

                # Process breaches
                for breach in breaches:
                    await self._handle_finding(breach, source='breach_db')

                # Check every hour
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"Error in breach monitoring: {e}")
                await asyncio.sleep(60)

    async def _digital_life_monitoring_loop(self):
        """
        Continuous digital life scanning
        """
        while self.monitoring:
            try:
                # Scan user's digital footprint
                issues = await self.digital_scanner.scan_privacy_issues()

                # Process issues
                for issue in issues:
                    await self._handle_finding(issue, source='digital_scan')

                # Scan every 24 hours
                await asyncio.sleep(24 * 3600)
            except Exception as e:
                logger.error(f"Error in digital life monitoring: {e}")
                await asyncio.sleep(60)

    async def _handle_finding(self, finding: Dict, source: str):
        """
        Handle a privacy finding
        """
        severity = self._calculate_severity(finding)

        finding_entry = {
            'finding': finding,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'severity': severity
        }

        # Add to findings
        self.findings.append(finding_entry)

        logger.warning(f"🚨 {severity.upper()} Privacy Alert from {source}: {finding}")

        # Auto-respond if possible
        await self.auto_responder.respond_to_finding(finding)

    def _calculate_severity(self, finding: Dict) -> str:
        """
        Calculate severity of finding
        """
        data_type = finding.get('type')

        # Critical: passwords, credit cards, SSN
        if data_type in ['password', 'credit_card', 'ssn', 'api_key']:
            return 'critical'
        # High: emails with passwords, phone numbers
        elif data_type in ['email_password_combo', 'phone_number']:
            return 'high'
        # Medium: emails, usernames
        elif data_type in ['email', 'username']:
            return 'medium'
        else:
            return 'low'

    async def add_monitored_data(self, data_type: str, value: str):
        """
        Add data to monitoring list
        """
        if data_type in self.monitored_data:
            if data_type == 'passwords':
                # Hash password before storing
                value = hashlib.sha256(value.encode()).hexdigest()

            self.monitored_data[data_type].add(value)
            logger.info(f"Added {data_type} to monitored data")

    async def get_summary(self) -> Dict:
        """
        Get privacy monitoring summary
        """
        return {
            'monitored_items': {
                k: len(v) for k, v in self.monitored_data.items()
            },
            'total_findings': len(self.findings),
            'status': "active" if self.monitoring else "inactive",
            'by_severity': {
                'critical': sum(1 for f in self.findings if f['severity'] == 'critical'),
                'high': sum(1 for f in self.findings if f['severity'] == 'high'),
                'medium': sum(1 for f in self.findings if f['severity'] == 'medium'),
                'low': sum(1 for f in self.findings if f['severity'] == 'low')
            },
            'recent_findings': self.findings[-10:] if self.findings else []
        }

    def get_status(self) -> Dict[str, Any]:
        """Return simplified status for system context"""
        return {
            "active": self.monitoring,
            "total_findings": len(self.findings)
        }

    async def stop(self):
        """
        Stop monitoring and cancel tasks
        """
        self.monitoring = False
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks = []
        logger.info("Privacy Guardian stopped")
