import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SmartDefaultsEngine:
    """
    Intelligently configure based on context
    """

    async def generate_config(self):
        """
        Generate smart default configuration
        """
        from epex.intelligence.detector import IntelligentProviderDetector
        detector = IntelligentProviderDetector()
        system = await detector.analyze_system()

        config = {
            # Model selection
            'primary_model': self._select_primary_model(system),
            'fallback_models': self._select_fallback_models(system),

            # Performance
            'max_concurrent_tasks': self._calculate_concurrency(system),
            'cache_size_mb': self._calculate_cache_size(system),

            # Behavior
            'auto_approve_low_risk': True,
            'require_approval_high_risk': True,

            # Features
            'enable_teach_mode': True,
            'enable_vision': True,
            'enable_voice': True,

            # Budget
            'daily_budget_usd': 10,
            'alert_at_percentage': 80
        }

        return config

    def _select_primary_model(self, system: dict):
        """
        Select best primary model based on system
        """
        keys = system.get('detected_keys', {})

        # Priority 1: High Quality if available
        if keys.get('openai'): return 'gpt-4o'
        if keys.get('anthropic'): return 'claude-3-5-sonnet-20240620'

        # Priority 2: Free Cloud
        if keys.get('google'): return 'gemini-1.5-flash'
        if keys.get('groq'): return 'llama-3.1-70b-versatile'

        # Priority 3: Local if capable
        if system['system_resources']['gpu'] and system['system_resources']['gpu_memory'] >= 8:
            return 'ollama/llama3.1'

        return 'gemini-1.5-flash' # Default recommendation

    def _select_fallback_models(self, system: dict):
        return ['llama-3-uncensored', 'mixtral-8x7b']

    def _calculate_concurrency(self, system: dict):
        cores = system['system_resources']['cpu_cores']
        return max(2, cores // 2)

    def _calculate_cache_size(self, system: dict):
        ram = system['system_resources']['ram']
        if ram >= 32: return 1024
        if ram >= 16: return 512
        return 256
