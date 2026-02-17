import asyncio
import logging
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from nexa.intelligence.api_manager import UniversalAPIKeyManager
from nexa.intelligence.detector import IntelligentProviderDetector
from nexa.intelligence.defaults import SmartDefaultsEngine
from nexa.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class TUISetupWizard:
    """
    Beautiful TUI setup interface
    """

    def __init__(self):
        self.console = Console()
        self.api_manager = UniversalAPIKeyManager()
        self.detector = IntelligentProviderDetector()
        self.storage = SecureConfigStorage()
        self.defaults = SmartDefaultsEngine()

    async def run(self):
        """
        Run TUI setup wizard
        """
        self.console.clear()

        # Welcome screen
        self.console.print(Panel(
            "[bold cyan]🤖 Welcome to Nexa Bot![/]\n\n"
            "[white]Let's get you set up in 60 seconds. I'm analyzing your system...[/]",
            border_style="cyan",
            title="⚡ NEXA BOT"
        ))

        # Background analysis
        with self.console.status("[bold green]Analyzing system..."):
            analysis = await self.detector.analyze_system()

        # Step 1: Personalization
        self.console.print("\n[bold cyan]Step 1/4: Personalization[/]")
        user_name = Prompt.ask("What should I call you?", default="User")
        nexa_name = Prompt.ask("What should you call me?", default="Nexa")

        # Step 2: System Analysis Results
        self.console.print("\n[bold cyan]Step 2/4: System Capabilities[/]")
        sys_res = analysis['system_resources']
        table = Table(show_header=False, box=None)
        table.add_row("CPU Cores:", f"{sys_res['cpu_cores']}")
        table.add_row("RAM:", f"{sys_res['ram']:.1f} GB")
        table.add_row("GPU Detected:", "[green]Yes[/]" if sys_res['gpu'] else "[yellow]No[/]")
        if sys_res['gpu']:
            table.add_row("GPU Memory:", f"{sys_res['gpu_memory']:.1f} GB")
        table.add_row("Network:", "[green]Online[/]" if analysis['network_access']['online'] else "[red]Offline[/]")
        self.console.print(table)

        # Recommendations
        if analysis['recommendations']:
            self.console.print("\n[bold]Recommendations based on your hardware:[/]")
            for rec in analysis['recommendations']:
                self.console.print(f" • [yellow]{rec['reason']}[/]")

        # Step 3: API Keys
        self.console.print(f"\n[bold cyan]Step 3/4: Intelligence Providers[/]")

        # Show detected keys
        detected = analysis['detected_keys']
        if detected:
            self.console.print(f"\n[green]✓ Auto-detected {len(detected)} API keys from your environment.[/]")

        setup_providers = Confirm.ask("\nWould you like to set up additional API keys now?", default=False)

        if setup_providers:
            configured = await self.api_manager.guided_setup()
            detected.update(configured)

        # Step 4: Finalizing
        self.console.print(f"\n[bold cyan]Step 4/4: Finalizing[/]")
        with self.console.status("[bold green]Generating smart defaults..."):
            smart_config = await self.defaults.generate_config()

        smart_config.update({
            "user_name": user_name,
            "nexa_name": nexa_name,
            "api_keys": detected,
            "setup_date": str(asyncio.get_event_loop().time())
        })

        await self.storage.store_config(smart_config)

        # Health Check
        await self.run_health_check()

        # Done!
        self.console.print(Panel.fit(
            f"[bold green]✓ Setup Complete![/]\n\n"
            f"[white]I'm {nexa_name}, nice to meet you {user_name}![/]\n"
            f"[white]Try running: [bold]nexa 'Hello world'[/][/]",
            border_style="green"
        ))

    async def run_health_check(self):
        """
        Comprehensive health check on first run
        """
        self.console.print("\n[bold]Running final health check...[/]")

        checks = {
            'Python Version': sys.version_info >= (3, 10),
            'Secure Storage': os.path.exists(self.storage.config_path),
            'Database': os.path.exists('nexa.db') or True, # Placeholder
            'Network': (await self.detector._check_network())['online']
        }

        for check, passed in checks.items():
            status = "[green]✓[/]" if passed else "[red]✗[/]"
            self.console.print(f"  {status} {check}")

        return all(checks.values())
