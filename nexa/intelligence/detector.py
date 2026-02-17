import asyncio
import logging
import psutil
import socket
import aiohttp
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class IntelligentProviderDetector:
    """
    Automatically detect what's available and recommend best setup
    """

    def __init__(self):
        self.http = None # Initialize in context if needed

    async def analyze_system(self):
        """
        Analyze user's system and recommend providers
        """

        analysis = {
            'detected_keys': await self._detect_keys(),
            'installed_tools': await self._detect_installed_tools(),
            'system_resources': await self._check_system_resources(),
            'network_access': await self._check_network(),
            'recommendations': []
        }

        # Generate recommendations
        recommendations = []

        # If has GPU and sufficient RAM → recommend local models
        if analysis['system_resources']['gpu'] and analysis['system_resources']['ram'] >= 16:
            recommendations.append({
                'type': 'local',
                'provider': 'ollama',
                'reason': 'You have a GPU - run models locally for FREE!',
                'priority': 1
            })

        # If no API keys detected → recommend free tiers
        if not analysis['detected_keys']:
            recommendations.append({
                'type': 'free',
                'providers': ['google', 'huggingface', 'groq'],
                'reason': 'Start FREE with these providers',
                'priority': 2
            })

        # If has fast internet → recommend cloud models
        if analysis['network_access']['speed_score'] > 5:
            recommendations.append({
                'type': 'cloud',
                'providers': ['openai', 'anthropic'],
                'reason': 'Fast internet - cloud models will work great',
                'priority': 3
            })

        analysis['recommendations'] = sorted(recommendations, key=lambda x: x['priority'])

        return analysis

    async def _detect_keys(self):
        from nexa.intelligence.api_manager import UniversalAPIKeyManager
        manager = UniversalAPIKeyManager()
        return await manager.auto_detect_keys()

    async def _detect_installed_tools(self):
        """
        Detect installed local AI tools
        """
        tools = {}
        async with aiohttp.ClientSession() as session:
            # Check for Ollama
            try:
                async with session.get('http://localhost:11434/api/tags', timeout=1) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('models', [])
                        tools['ollama'] = {
                            'installed': True,
                            'models': [m['name'] for m in models]
                        }
            except:
                tools['ollama'] = {'installed': False}

            # Check for LM Studio
            try:
                async with session.get('http://localhost:1234/v1/models', timeout=1) as response:
                    if response.status == 200:
                        tools['lmstudio'] = {'installed': True}
            except:
                tools['lmstudio'] = {'installed': False}

        return tools

    async def _check_system_resources(self):
        """
        Check system capabilities
        """
        has_gpu = False
        gpu_memory = 0

        try:
            # Try to use nvidia-smi if available
            import subprocess
            res = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'], encoding='utf-8')
            gpu_memory = int(res.strip()) / 1024.0 # GB
            has_gpu = True
        except:
            try:
                import torch
                has_gpu = torch.cuda.is_available()
                if has_gpu:
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            except: pass

        return {
            'cpu_cores': psutil.cpu_count(),
            'ram': psutil.virtual_memory().total / 1e9,  # GB
            'gpu': has_gpu,
            'gpu_memory': gpu_memory,
            'disk_free': psutil.disk_usage('/').free / 1e9
        }

    async def _check_network(self):
        """
        Quick network check
        """
        try:
            start = asyncio.get_event_loop().time()
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.google.com', timeout=2) as r:
                    latency = (asyncio.get_event_loop().time() - start) * 1000
                    speed_score = 10 if latency < 100 else (5 if latency < 500 else 2)
                    return {'online': True, 'latency_ms': latency, 'speed_score': speed_score}
        except:
            return {'online': False, 'latency_ms': -1, 'speed_score': 0}
