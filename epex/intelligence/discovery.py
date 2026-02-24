"""
HuggingFace Model Discovery System for EPEX APEX v5.0
Autonomously scans, categorizes, and registers the latest AI models.
"""

import asyncio
import aiohttp
import logging
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from epex.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class ModelDiscoverySystem:
    """Autonomously discovers and categorizes models from HuggingFace"""

    def __init__(self):
        self.storage = SecureConfigStorage()
        self.hf_api_url = "https://huggingface.co/api/models"
        self.categories = {
            'text': ['text-generation', 'summarization', 'translation', 'feature-extraction'],
            'image': ['text-to-image', 'image-to-text', 'image-classification', 'object-detection'],
            'audio': ['text-to-speech', 'speech-to-text', 'audio-classification'],
            'video': ['video-classification', 'text-to-video'],
            'multimodal': ['visual-question-answering', 'document-question-answering'],
            'code': ['code-generation']
        }

    async def run_discovery(self, days_back: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """Scan HuggingFace for trending models from the last N days"""
        discovered = {cat: [] for cat in self.categories.keys()}
        discovered['other'] = []

        # Get HF Key if available
        config = await self.storage.load_config()
        hf_key = config.get('api_keys', {}).get('huggingface')
        if isinstance(hf_key, list) and hf_key: hf_key = hf_key[0]

        headers = {"Authorization": f"Bearer {hf_key}"} if hf_key else {}

        # We search for models sorted by downloads to find trending ones
        params = {
            'sort': 'downloads',
            'direction': -1,
            'limit': 50
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.hf_api_url, params=params, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        models = await resp.json()
                        for m in models:
                            model_id = m['id']
                            pipeline_tag = m.get('pipeline_tag', 'unknown')

                            category = 'other'
                            for cat, tags in self.categories.items():
                                if pipeline_tag in tags:
                                    category = cat
                                    break

                            model_info = {
                                'id': model_id,
                                'name': model_id.split('/')[-1],
                                'author': m.get('author', 'unknown'),
                                'downloads': m.get('downloads', 0),
                                'likes': m.get('likes', 0),
                                'pipeline': pipeline_tag,
                                'last_modified': m.get('lastModified'),
                                'tags': m.get('tags', [])
                            }

                            # Check if already discovered or known
                            if not self._is_already_known(config, model_id):
                                discovered[category].append(model_info)

                        # Store newly discovered in 'pending_approval'
                        if any(discovered.values()):
                            await self._store_pending(config, discovered)

                        return discovered
                    else:
                        logger.error(f"HF Discovery API error: {resp.status}")
                        return discovered
        except Exception as e:
            logger.error(f"Model Discovery failed: {e}")
            return discovered

    def _is_already_known(self, config, model_id):
        # Check discovered_models
        discovered = config.get('discovered_models', {})
        for p_models in discovered.values():
            if any(m['id'] == model_id for m in p_models):
                return True

        # Check pending
        pending = config.get('pending_discovery', {})
        for p_list in pending.values():
            if any(m['id'] == model_id for m in p_list):
                return True

        return False

    async def _store_pending(self, config, discovered):
        pending = config.get('pending_discovery', {})
        for cat, models in discovered.items():
            if cat not in pending: pending[cat] = []
            pending[cat].extend(models)

        config['pending_discovery'] = pending
        await self.storage.store_config(config)

    async def auto_approve_popular(self, download_threshold: int = 5000):
        """Automatically approve high-quality/popular models"""
        config = await self.storage.load_config()
        pending = config.get('pending_discovery', {})
        new_pending = {}
        approved_count = 0

        for cat, models in pending.items():
            remaining = []
            for m in models:
                if m.get('downloads', 0) >= download_threshold:
                    await self.approve_model(m['id'], category=cat, config=config)
                    approved_count += 1
                else:
                    remaining.append(m)
            if remaining:
                new_pending[cat] = remaining

        if approved_count > 0:
            config['pending_discovery'] = new_pending
            await self.storage.store_config(config)
            logger.info(f"Auto-approved {approved_count} popular models.")

        return approved_count

    async def approve_model(self, model_id: str, category: str = None, config: dict = None):
        """Register an approved model into the system registry"""
        if config is None:
            config = await self.storage.load_config()

        # Move from pending to discovered
        pending = config.get('pending_discovery', {})
        model_data = None

        for cat, models in pending.items():
            for i, m in enumerate(models):
                if m['id'] == model_id:
                    model_data = m
                    models.pop(i)
                    break
            if model_data: break

        if not model_data:
            # Maybe it wasn't in pending? Or we just have the ID
            model_data = {'id': model_id, 'capabilities': [category] if category else ['chat']}

        if 'discovered_models' not in config: config['discovered_models'] = {}
        if 'huggingface' not in config['discovered_models']: config['discovered_models']['huggingface'] = []

        # Check for duplicates
        if not any(m['id'] == model_id for m in config['discovered_models']['huggingface']):
            config['discovered_models']['huggingface'].append(model_data)

        await self.storage.store_config(config)
        return True

    async def get_pending_report(self) -> Dict[str, List[Dict[str, Any]]]:
        config = await self.storage.load_config()
        return config.get('pending_discovery', {})
