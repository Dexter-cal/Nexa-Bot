from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
import asyncio
from nexa.intelligence.api_manager import UniversalAPIKeyManager
from nexa.intelligence.detector import IntelligentProviderDetector
from nexa.foundation.storage import SecureConfigStorage

class TUISetupWizard:
    """
    Beautiful TUI setup interface
    """

    def __init__(self):
        self.console = Console()
        self.api_manager = UniversalAPIKeyManager()
        self.detector = IntelligentProviderDetector()
        self.storage = SecureConfigStorage()

    async def run(self):
        """
        Run TUI setup wizard
        """

        # Welcome screen
        self.console.print(Panel.fit(
            "[bold cyan]🤖 Welcome to Nexa Bot![/]\n\n"
            "[white]Let's get you set up in 60 seconds[/]",
            border_style="cyan"
        ))

        # Step 1: Name
        self.console.print("\n[bold]Step 1/3:[/] What should I call you?")
        user_name = Prompt.ask("[cyan]Your name[/]", default="User")

        self.console.print("\n[bold]Step 2/3:[/] What should you call me?")
        nexa_name = Prompt.ask("[cyan]My name[/]", default="Nexa")

        # Step 3: API Keys
        self.console.print(f"\n[bold]Step 3/3:[/] Let's set up API keys")

        # Show detected keys
        detected = await self.api_manager.auto_detect_keys()

        if detected:
            table = Table(title="Auto-Detected API Keys")
            table.add_column("Provider", style="cyan")
            table.add_column("Status", style="green")

            for provider in detected:
                table.add_row(
                    self.api_manager.providers[provider]['name'],
                    "✓ Valid"
                )

            self.console.print(table)

        # Show recommendations
        self.console.print("\n[bold cyan]Recommended FREE providers:[/]")
        self.console.print("1. Google AI Studio (60 req/min FREE)")
        self.console.print("2. HuggingFace (1000+ models FREE)")
        self.console.print("3. Groq (14,400 req/day FREE)")

        setup_providers = Confirm.ask("\nSet up additional providers now?", default=True)

        config = {
            "user_name": user_name,
            "nexa_name": nexa_name,
            "api_keys": detected
        }

        if setup_providers:
            recommended = ['google', 'huggingface', 'groq', 'openai', 'anthropic']
            for provider_id in recommended:
                if provider_id in detected:
                    continue

                info = self.api_manager.providers[provider_id]
                if Confirm.ask(f"Set up {info['name']}?"):
                    self.console.print(f"Get your key here: [link={info['get_key_url']}]{info['get_key_url']}[/link]")
                    key = Prompt.ask(f"Enter {info['name']} API Key", password=True)
                    if key:
                        self.console.print(f"Testing {info['name']} key...")
                        is_valid = await self.api_manager.test_api_key(provider_id, key)
                        if is_valid:
                            self.console.print(f"[green]✓ {info['name']} key is valid![/]")
                            config['api_keys'][provider_id] = key
                        else:
                            self.console.print(f"[red]✗ {info['name']} key validation failed. Skipping.[/]")

        # Save config
        await self.storage.store_config(config)

        # Done!
        self.console.print(Panel.fit(
            f"[bold green]✓ Setup Complete![/]\n\n"
            f"[white]I'm {nexa_name}, nice to meet you {user_name}![/]\n"
            f"[white]Try: nexa 'Hello world'[/]",
            border_style="green"
        ))
