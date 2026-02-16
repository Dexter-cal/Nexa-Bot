import os
import json
import logging
import aiohttp
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
                'models': ['claude-sonnet-4', 'claude-opus-4']
            },

            'google': {
                'name': 'Google AI Studio',
                'key_format': 'AIza...',
                'test_endpoint': 'https://generativelanguage.googleapis.com/v1/models',
                'get_key_url': 'https://makersuite.google.com/app/apikey',
                'free_tier': True,
                'free_limit': '60 requests/minute',
                'cost': 'FREE → $',
                'models': ['gemini-2.0-flash', 'gemini-2.0-pro'],
                'recommended': True  # Recommend for free tier
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
                'recommended': True  # Recommend for free tier
            },

            'groq': {
                'name': 'Groq',
                'key_format': 'gsk_...',
                'test_endpoint': 'https://api.groq.com/openai/v1/models',
                'get_key_url': 'https://console.groq.com/keys',
                'free_tier': True,
                'free_limit': '14,400 requests/day',
                'cost': 'FREE',
                'models': ['llama-3.3-70b', 'mixtral-8x7b'],
                'recommended': True
            },

            'deepseek': {
                'name': 'DeepSeek',
                'key_format': 'sk-...',
                'test_endpoint': 'https://api.deepseek.com/v1/models',
                'get_key_url': 'https://platform.deepseek.com/api_keys',
                'free_tier': True,
                'cost': 'FREE → $',
                'models': ['deepseek-v3', 'deepseek-coder']
            },

            'ollama': {
                'name': 'Ollama (Local)',
                'key_format': None,  # No key needed
                'test_endpoint': 'http://localhost:11434/api/tags',
                'get_key_url': 'https://ollama.ai/download',
                'free_tier': True,
                'cost': 'FREE (runs locally)',
                'models': 'All Ollama models',
                'recommended': True,
                'requires_install': True
            },

            'telegram': {
                'name': 'Telegram Bot',
                'key_format': '...:...',
                'test_endpoint': 'https://api.telegram.org/bot{key}/getMe',
                'get_key_url': 'https://t.me/BotFather',
                'free_tier': True,
                'cost': 'FREE'
            }
        }

    async def auto_detect_keys(self):
        """
        Automatically detect API keys from environment
        """

        detected = {}

        # Check environment variables
        env_patterns = {
            'openai': ['OPENAI_API_KEY', 'OPENAI_KEY'],
            'anthropic': ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY'],
            'google': ['GOOGLE_API_KEY', 'GEMINI_API_KEY'],
            'huggingface': ['HUGGINGFACE_TOKEN', 'HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN'],
            'groq': ['GROQ_API_KEY'],
            'deepseek': ['DEEPSEEK_API_KEY'],
            'telegram': ['TELEGRAM_BOT_TOKEN']
        }

        for provider, patterns in env_patterns.items():
            for pattern in patterns:
                key = os.getenv(pattern)
                if key:
                    detected[provider] = key
                    break

        # Also check .env file if it exists
        try:
            from dotenv import load_dotenv
            load_dotenv()
            for provider, patterns in env_patterns.items():
                if provider in detected: continue
                for pattern in patterns:
                    key = os.getenv(pattern)
                    if key:
                        detected[provider] = key
                        break
        except ImportError:
            pass

        # Finally check secure storage
        try:
            stored_config = await self.vault.load_config()
            stored_keys = stored_config.get('api_keys', {})
            for provider, key in stored_keys.items():
                if provider not in detected:
                    detected[provider] = key
        except Exception as e:
            logger.error(f"Failed to load keys from secure storage: {e}")

        return detected

    async def test_api_key(self, provider: str, key: str):
        """
        Test if API key is valid
        """

        info = self.providers[provider]

        async with aiohttp.ClientSession() as session:
            try:
                if provider == 'openai':
                    async with session.get(
                        info['test_endpoint'],
                        headers={'Authorization': f'Bearer {key}'}
                    ) as response:
                        return response.status == 200

                elif provider == 'anthropic':
                    async with session.post(
                        info['test_endpoint'],
                        headers={
                            'x-api-key': key,
                            'anthropic-version': '2023-06-01'
                        },
                        json={
                            'model': 'claude-3-sonnet-20240229',
                            'max_tokens': 1,
                            'messages': [{'role': 'user', 'content': 'Hi'}]
                        }
                    ) as response:
                        return response.status == 200

                elif provider == 'google':
                    async with session.get(
                        f"{info['test_endpoint']}?key={key}"
                    ) as response:
                        return response.status == 200

                elif provider == 'huggingface':
                    async with session.get(
                        info['test_endpoint'],
                        headers={'Authorization': f'Bearer {key}'}
                    ) as response:
                        return response.status == 200

                return False

            except Exception as e:
                logger.error(f"API key test failed for {provider}: {e}")
                return False

    async def _input_secret(self, prompt="Enter API Key: "):
        from rich.prompt import Prompt
        return Prompt.ask(prompt, password=True)

    async def _ask_yes_no(self, question, default=True):
        from rich.prompt import Confirm
        return Confirm.ask(question, default=default)

    async def _multi_select(self, options):
        """
        Simplified multi-select using Prompt
        """
        from rich.console import Console
        console = Console()

        console.print("\nAvailable options:")
        for i, opt in enumerate(options):
            console.print(f"{i+1}. {opt['label']}")

        indices = Console().input("\nEnter numbers separated by space (e.g. 1 3): ")
        selected = []
        try:
            for idx in indices.split():
                selected.append(options[int(idx)-1]['value'])
        except (ValueError, IndexError):
            console.print("[red]Invalid selection.[/]")

        return selected
