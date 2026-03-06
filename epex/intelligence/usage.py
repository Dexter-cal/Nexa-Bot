import json
import logging
import time
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class UsageTracker:
    """
    Track token usage and costs for all providers
    """
    def __init__(self):
        self.stats_path = Path.home() / '.epex' / 'usage_stats.json'
        self.stats = self._load_stats()

    def _load_stats(self):
        if self.stats_path.exists():
            try:
                return json.loads(self.stats_path.read_text())
            except:
                return {}
        return {}

    def _save_stats(self):
        try:
            self.stats_path.parent.mkdir(parents=True, exist_ok=True)
            self.stats_path.write_text(json.dumps(self.stats))
        except Exception as e:
            logger.error(f"Failed to save usage stats: {e}")

    def record_usage(self, model: str, provider: str, tokens: int, cost: float):
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats:
            self.stats[today] = {
                'total_cost': 0.0,
                'total_tokens': 0,
                'models': {},
                'providers': {}
            }

        day_stats = self.stats[today]
        day_stats['total_cost'] += cost
        day_stats['total_tokens'] += tokens

        if model not in day_stats['models']:
            day_stats['models'][model] = {'tokens': 0, 'cost': 0.0}
        day_stats['models'][model]['tokens'] += tokens
        day_stats['models'][model]['cost'] += cost

        if provider not in day_stats['providers']:
            day_stats['providers'][provider] = {'tokens': 0, 'cost': 0.0}
        day_stats['providers'][provider]['tokens'] += tokens
        day_stats['providers'][provider]['cost'] += cost

        self._save_stats()

    def get_today_stats(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return self.stats.get(today, {
            'total_cost': 0.0,
            'total_tokens': 0,
            'models': {},
            'providers': {}
        })

class BudgetManager:
    """
    Manage daily budget and limits
    """
    def __init__(self, tracker: UsageTracker):
        self.tracker = tracker
        self.config_path = Path.home() / '.epex' / 'budget_config.json'
        self.config = self._load_config()

    def _load_config(self):
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text())
            except:
                return {'daily_limit': 10.0}
        return {'daily_limit': 10.0}

    def set_limit(self, limit: float):
        self.config['daily_limit'] = limit
        self.config_path.write_text(json.dumps(self.config))

    def is_over_budget(self) -> bool:
        stats = self.tracker.get_today_stats()
        return stats['total_cost'] >= self.config['daily_limit']

    def get_remaining_budget(self) -> float:
        stats = self.tracker.get_today_stats()
        return max(0.0, self.config['daily_limit'] - stats['total_cost'])
