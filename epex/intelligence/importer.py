import json
import os
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

class ConfigImporter:
    """
    Import configuration from other AI tools
    """

    async def import_all(self) -> Dict[str, str]:
        keys = {}
        keys.update(await self.import_from_cursor())
        keys.update(await self.import_from_continue())
        keys.update(await self.import_from_vscode())
        return keys

    async def import_from_cursor(self):
        """
        Import API keys from Cursor IDE
        """
        keys = {}
        paths = [
            Path.home() / 'Library' / 'Application Support' / 'Cursor' / 'User' / 'settings.json',
            Path.home() / '.config' / 'Cursor' / 'User' / 'settings.json',
            Path(os.getenv('APPDATA', '')) / 'Cursor' / 'User' / 'settings.json'
        ]

        for path in paths:
            if path.exists():
                try:
                    with open(path) as f:
                        config = json.load(f)

                    if 'openai.apiKey' in config:
                        keys['openai'] = config['openai.apiKey']
                    if 'anthropic.apiKey' in config:
                        keys['anthropic'] = config['anthropic.apiKey']
                except: pass
        return keys

    async def import_from_continue(self):
        """
        Import from Continue.dev
        """
        keys = {}
        path = Path.home() / '.continue' / 'config.json'
        if path.exists():
            try:
                with open(path) as f:
                    config = json.load(f)
                # Parse continue config for keys (simplified)
                models = config.get('models', [])
                for model in models:
                    if 'apiKey' in model:
                        provider = model.get('provider', '')
                        if provider in ['openai', 'anthropic', 'google', 'mistral']:
                            keys[provider] = model['apiKey']
            except: pass
        return keys

    async def import_from_vscode(self):
        # Similar logic for VSCode Copilot or other extensions
        return {}
