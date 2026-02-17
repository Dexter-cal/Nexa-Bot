import os
import json
import logging
import asyncio
import aiohttp
import re
from nexa.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class UniversalAPIKeyManager:
    """
    Manage API keys for ALL providers in one place
    """

    def __init__(self):
        self.vault = SecureConfigStorage()
        self.http = None # Initialize in async context if needed

        # ALL supported providers
        self.providers = {
            # Commercial LLMs
            'openai': {
                'name': 'OpenAI',
                'key_format': 'sk-...',
                'test_endpoint': 'https://api.openai.com/v1/models',
                'get_key_url': 'https://platform.openai.com/api-keys',
                'free_tier': False,
                'cost': '$$$',
                'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo']
            },

            'anthropic': {
                'name': 'Anthropic (Claude)',
                'key_format': 'sk-ant-...',
                'test_endpoint': 'https://api.anthropic.com/v1/messages',
                'get_key_url': 'https://console.anthropic.com/settings/keys',
                'free_tier': False,
                'cost': '$$$',
                'models': ['claude-3-5-sonnet-20240620', 'claude-3-opus-20240229']
            },

            'google': {
                'name': 'Google AI Studio',
                'key_format': 'AIza...',
                'test_endpoint': 'https://generativelanguage.googleapis.com/v1/models',
                'get_key_url': 'https://aistudio.google.com/app/apikey',
                'free_tier': True,
                'free_limit': '60 requests/minute',
                'cost': 'FREE → $',
                'models': ['gemini-1.5-flash', 'gemini-1.5-pro'],
                'recommended': True
            },

            'huggingface': {
                'name': 'HuggingFace',
                'key_format': 'hf_...',
                'test_endpoint': 'https://huggingface.co/api/whoami-v2',
                'get_key_url': 'https://huggingface.co/settings/tokens',
                'free_tier': True,
                'free_limit': 'Unlimited (rate limited)',
                'cost': 'FREE',
                'models': '1000+ models available',
                'recommended': True
            },

            'groq': {
                'name': 'Groq',
                'key_format': 'gsk_...',
                'test_endpoint': 'https://api.groq.com/openai/v1/models',
                'get_key_url': 'https://console.groq.com/keys',
                'free_tier': True,
                'free_limit': '14,400 requests/day',
                'cost': 'FREE',
                'models': ['llama-3.1-70b-versatile', 'mixtral-8x7b-32768'],
                'recommended': True
            },

            'deepseek': {
                'name': 'DeepSeek',
                'key_format': 'sk-...',
                'test_endpoint': 'https://api.deepseek.com/v1/models',
                'get_key_url': 'https://platform.deepseek.com/api_keys',
                'free_tier': True,
                'cost': 'FREE → $',
                'models': ['deepseek-chat', 'deepseek-coder']
            },

            'mistral': {
                'name': 'Mistral AI',
                'key_format': '...',
                'test_endpoint': 'https://api.mistral.ai/v1/models',
                'get_key_url': 'https://console.mistral.ai/api-keys',
                'free_tier': False,
                'cost': '$$',
                'models': ['mistral-large-latest', 'open-mixtral-8x22b']
            },

            'together': {
                'name': 'Together AI',
                'key_format': '...',
                'test_endpoint': 'https://api.together.xyz/models',
                'get_key_url': 'https://api.together.xyz/settings/api-keys',
                'free_tier': True,
                'free_limit': '$25 credit',
                'cost': 'FREE → $',
                'models': '100+ open source models'
            },

            'replicate': {
                'name': 'Replicate',
                'key_format': 'r8_...',
                'test_endpoint': 'https://api.replicate.com/v1/models',
                'get_key_url': 'https://replicate.com/account/api-tokens',
                'free_tier': True,
                'cost': 'Pay per use',
                'models': '1000+ models'
            },

            # Local/Open Source
            'ollama': {
                'name': 'Ollama (Local)',
                'key_format': None,
                'test_endpoint': 'http://localhost:11434/api/tags',
                'get_key_url': 'https://ollama.ai/download',
                'free_tier': True,
                'cost': 'FREE (runs locally)',
                'models': 'All Ollama models',
                'recommended': True,
                'requires_install': True
            },

            'lmstudio': {
                'name': 'LM Studio (Local)',
                'key_format': None,
                'test_endpoint': 'http://localhost:1234/v1/models',
                'get_key_url': 'https://lmstudio.ai',
                'free_tier': True,
                'cost': 'FREE (runs locally)',
                'requires_install': True
            },

            # Communication
            'telegram': {
                'name': 'Telegram Bot',
                'key_format': '...:...',
                'test_endpoint': 'https://api.telegram.org/bot{key}/getMe',
                'get_key_url': 'https://t.me/BotFather',
                'free_tier': True,
                'cost': 'FREE'
            },

            'twilio': {
                'name': 'Twilio (Calls/SMS)',
                'key_format': 'account_sid + auth_token',
                'test_endpoint': 'https://api.twilio.com/2010-04-01/Accounts',
                'get_key_url': 'https://www.twilio.com/console',
                'free_tier': True,
                'free_limit': 'Trial credit'
            }
        }

    async def auto_detect_keys(self):
        """
        Automatically detect API keys from environment
        """
        detected = {}
        env_patterns = {
            'openai': ['OPENAI_API_KEY', 'OPENAI_KEY'],
            'anthropic': ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY'],
            'google': ['GOOGLE_API_KEY', 'GEMINI_API_KEY'],
            'huggingface': ['HUGGINGFACE_TOKEN', 'HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN'],
            'groq': ['GROQ_API_KEY'],
            'deepseek': ['DEEPSEEK_API_KEY'],
            'telegram': ['TELEGRAM_BOT_TOKEN'],
            'mistral': ['MISTRAL_API_KEY'],
            'together': ['TOGETHER_API_KEY'],
            'replicate': ['REPLICATE_API_TOKEN']
        }

        for provider, patterns in env_patterns.items():
            for pattern in patterns:
                key = os.getenv(pattern)
                if key:
                    detected[provider] = key
                    break

        # Check common config files (Mocked/Simplified)
        config_paths = [
            '~/.openai/api_key',
            '~/.anthropic/api_key',
            '~/.config/huggingface/token'
        ]
        for path in config_paths:
            full_path = os.path.expanduser(path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r') as f:
                        key = f.read().strip()
                        if key:
                            # Map path to provider
                            if 'openai' in path: detected['openai'] = key
                            elif 'anthropic' in path: detected['anthropic'] = key
                            elif 'huggingface' in path: detected['huggingface'] = key
                except: pass

        # Load from secure storage
        try:
            stored = await self.vault.load_config()
            if 'api_keys' in stored:
                for p, k in stored['api_keys'].items():
                    if p not in detected:
                        detected[p] = k
        except: pass

        return detected

    async def guided_setup(self):
        """
        Interactive guided setup for API keys
        """
        from rich.console import Console
        console = Console()

        console.print("[bold cyan]🔑 API Key Setup[/]\n")

        # Auto-detect first
        detected = await self.auto_detect_keys()

        if detected:
            console.print(f"✓ Auto-detected {len(detected)} API keys:")
            for provider in detected:
                console.print(f"  • {self.providers[provider]['name']}")
            console.print()

        # Show recommendations
        console.print("📝 Recommended Providers (FREE tier available):\n")

        recommended = [
            p for p, info in self.providers.items()
            if info.get('recommended', False)
        ]

        for provider in recommended:
            info = self.providers[provider]
            status = "✓ Detected" if provider in detected else "  Setup"
            console.print(f"{status} {info['name']}")
            console.print(f"       Cost: {info['cost']}")
            if info.get('free_limit'):
                console.print(f"       Free: {info['free_limit']}")
            console.print()

        # Ask which to configure
        console.print("Which providers would you like to set up?")
        console.print("(You can add more later in settings)")

        choices = await self._multi_select([
            {'value': p, 'label': f"{info['name']} ({info['cost']})", 'default': p in detected}
            for p, info in self.providers.items()
            if not info.get('requires_install')
        ])

        configured = {}
        for provider in choices:
            if provider in detected:
                valid = await self.test_api_key(provider, detected[provider])
                if valid:
                    configured[provider] = detected[provider]
                    console.print(f"✓ {self.providers[provider]['name']}: Valid")
                else:
                    console.print(f"✗ {self.providers[provider]['name']}: Invalid, please enter manually")
                    key = await self._get_key_manual(provider)
                    if key: configured[provider] = key
            else:
                key = await self._get_key_manual(provider)
                if key: configured[provider] = key

        # Save to vault
        if configured:
            current_config = await self.vault.load_config()
            api_keys = current_config.get('api_keys', {})
            api_keys.update(configured)
            current_config['api_keys'] = api_keys
            await self.vault.store_config(current_config)

        return configured

    async def _get_key_manual(self, provider: str):
        """
        Get API key manually from user
        """
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        console = Console()
        info = self.providers[provider]

        console.print(f"\n🔑 {info['name']} Setup")
        console.print(f"Get your API key: [link={info['get_key_url']}]{info['get_key_url']}[/link]")

        open_browser = Confirm.ask("Open in browser?", default=True)
        if open_browser:
            import webbrowser
            webbrowser.open(info['get_key_url'])

        console.print(f"\nEnter your {info['name']} API key (Format: {info['key_format']}):")
        key = Prompt.ask("API Key", password=True)

        # Test key
        console.print("Testing API key...")
        valid = await self.test_api_key(provider, key)

        if valid:
            console.print(f"✓ {info['name']} API key is valid!")
            return key
        else:
            console.print(f"✗ API key test failed")
            retry = Confirm.ask("Try again?", default=True)
            if retry:
                return await self._get_key_manual(provider)
            return None

    async def test_api_key(self, provider: str, key: str):
        """
        Test if API key is valid
        """
        info = self.providers[provider]
        try:
            async with aiohttp.ClientSession() as session:
                if provider == 'openai':
                    async with session.get(info['test_endpoint'], headers={'Authorization': f'Bearer {key}'}) as r:
                        return r.status == 200
                elif provider == 'anthropic':
                    async with session.post(info['test_endpoint'], headers={'x-api-key': key, 'anthropic-version': '2023-06-01'},
                                           json={'model': 'claude-3-haiku-20240307', 'max_tokens': 1, 'messages': [{'role': 'user', 'content': 'Hi'}]}) as r:
                        return r.status == 200
                elif provider == 'google':
                    async with session.get(f"{info['test_endpoint']}?key={key}") as r:
                        return r.status == 200
                elif provider == 'huggingface':
                    async with session.get(info['test_endpoint'], headers={'Authorization': f'Bearer {key}'}) as r:
                        return r.status == 200
                elif provider == 'groq':
                    async with session.get(info['test_endpoint'], headers={'Authorization': f'Bearer {key}'}) as r:
                        return r.status == 200
                elif provider == 'deepseek':
                    async with session.get(info['test_endpoint'], headers={'Authorization': f'Bearer {key}'}) as r:
                        return r.status == 200
                return False
        except Exception as e:
            logger.error(f"API key test failed for {provider}: {e}")
            return False

    async def _multi_select(self, options):
        from rich.console import Console
        console = Console()
        console.print("\nAvailable providers:")
        for i, opt in enumerate(options):
            status = "[green](detected)[/]" if opt.get('default') else ""
            console.print(f" {i+1}. {opt['label']} {status}")

        console.print("\nEnter numbers separated by space (e.g. 1 3):")
        indices = input("> ")
        selected = []
        try:
            for idx in indices.split():
                selected.append(options[int(idx)-1]['value'])
        except:
            console.print("[red]Invalid selection.[/]")
        return selected
