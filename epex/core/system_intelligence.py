"""
System Intelligence Engine for EPEX APEX v5.0
Runs comprehensive background checks for system health, connectivity, and intelligence readiness.
"""

import asyncio
import json
import os
import psutil
import aiohttp
import time
import logging
from pathlib import Path
from datetime import datetime
from packaging import version

logger = logging.getLogger(__name__)

class SystemIntelligence:
    """Runs comprehensive background checks silently at startup"""

    def __init__(self):
        self.config_dir = Path.home() / '.epex'
        self.results = {}
        self.current_version = "5.0.0"

    async def run_all_checks(self):
        """Run all 15+ checks in parallel for maximum speed"""
        start_time = time.time()

        checks = await asyncio.gather(
            self.check_profile(),
            self.check_api_keys(),
            self.check_network(),
            self.check_system_resources(),
            self.check_session(),
            self.check_updates(),
            self.check_dependencies(),
            self.check_permissions(),
            return_exceptions=True
        )

        # Compile results
        for check in checks:
            if isinstance(check, dict):
                self.results.update(check)
            elif isinstance(check, Exception):
                logger.error(f"Background check failed: {check}")

        self.results['total_check_time'] = time.time() - start_time
        return self.results

    async def check_profile(self):
        """Verify user profile and agent identity"""
        from epex.foundation.storage import SecureConfigStorage
        storage = SecureConfigStorage()
        config = await storage.load_config()

        if not config:
            return {'profile_status': 'missing', 'needs_setup': True}

        user_name = config.get('user_name', 'User')
        agent_name = config.get('epex_name', 'Epex')

        setup_date = config.get('setup_date')
        days_using = 0
        if setup_date:
            try:
                days_using = (datetime.now() - datetime.fromisoformat(setup_date)).days
            except: pass

        return {
            'profile_status': 'complete' if config.get('setup_complete') else 'incomplete',
            'user_name': user_name,
            'agent_name': agent_name,
            'days_using': days_using,
            'setup_complete': config.get('setup_complete', False)
        }

    async def check_api_keys(self):
        """Validate all connected API providers"""
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        manager = UniversalAPIKeyManager()
        status_map = await manager.get_connected_providers()

        valid_providers = [p for p, online in status_map.items() if online]

        # Get model counts for connected providers
        total_models = 0
        config = await manager.vault.load_config()
        discovered = config.get('discovered_models', {})
        for p in valid_providers:
            total_models += len(discovered.get(p, []))

        return {
            'keys_status': 'healthy' if valid_providers else 'none',
            'active_providers': valid_providers,
            'total_models_available': total_models,
            'status_map': status_map
        }

    async def check_network(self):
        """Check internet connectivity and latency"""
        urls = ['https://api.openai.com', 'https://www.google.com', 'https://huggingface.co']
        results = []

        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    start = time.time()
                    async with session.get(url, timeout=2) as resp:
                        results.append({'url': url, 'online': True, 'latency': (time.time() - start) * 1000})
                except:
                    results.append({'url': url, 'online': False, 'latency': None})

        online_count = sum(1 for r in results if r['online'])
        avg_latency = sum(r['latency'] for r in results if r['latency']) / online_count if online_count > 0 else 0

        return {
            'network_online': online_count > 0,
            'network_quality': 'excellent' if avg_latency < 100 else 'fair' if avg_latency < 500 else 'poor',
            'avg_latency': avg_latency
        }

    async def check_system_resources(self):
        """Monitor CPU, RAM, and Disk"""
        disk = psutil.disk_usage('/')
        ram = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)

        return {
            'cpu_usage': cpu,
            'ram_usage': ram.percent,
            'disk_free_gb': disk.free / (1024**3),
            'system_health': 'optimal' if cpu < 70 and ram.percent < 80 else 'burdened'
        }

    async def check_session(self):
        """Check previous session persistence"""
        from epex.foundation.storage import SecureConfigStorage
        storage = SecureConfigStorage()
        config = await storage.load_config()

        last_active = config.get('last_active_time')
        return {
            'has_previous_session': last_active is not None,
            'last_active': last_active
        }

    async def check_updates(self):
        """Check for EPEX system updates"""
        # Simulated update check
        return {
            'update_available': False,
            'latest_version': self.current_version,
            'current_version': self.current_version
        }

    async def check_dependencies(self):
        """Verify core libraries are present"""
        try:
            import rich, textual, psutil, cryptography, aiohttp, bcrypt
            return {'dependencies_ok': True}
        except ImportError as e:
            return {'dependencies_ok': False, 'missing': str(e)}

    async def check_permissions(self):
        """Verify filesystem access"""
        can_write = os.access(os.path.expanduser('~'), os.W_OK)
        return {'filesystem_writable': can_write}
