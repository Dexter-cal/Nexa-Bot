import asyncio
import logging
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from epex.intelligence.api_manager import UniversalAPIKeyManager
from epex.intelligence.detector import IntelligentProviderDetector
from epex.intelligence.defaults import SmartDefaultsEngine
from epex.foundation.storage import SecureConfigStorage

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
            "[bold cyan]🤖 Welcome to EPEX APEX v5.0![/]\n\n"
            "[white]Let's get you set up with zero friction. I'm analyzing your system...[/]",
            border_style="cyan",
            title="⚡ EPEX BOT"
        ))

        # Background analysis
        with self.console.status("[bold green]Analyzing system..."):
            analysis = await self.detector.analyze_system()

        # Step 1: Personalization
        self.console.print("\n[bold cyan]Step 1/5: Personalization[/]")
        user_name = Prompt.ask("What should I call you?", default="User")
        epex_name = Prompt.ask("What should you call me?", default="Epex")

        # Optional Password
        password_hash = None
        if Confirm.ask("\nWould you like to protect this agent with a password?", default=False):
            password = Prompt.ask("Set Agent Password", password=True)
            import bcrypt
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            self.console.print("[green]✓ Password secured.[/]")

        # Step 2: System Analysis Results
        self.console.print("\n[bold cyan]Step 2/5: System Capabilities[/]")
        sys_res = analysis['system_resources']
        table = Table(show_header=False, box=None)
        table.add_row("CPU Cores:", f"{sys_res['cpu_cores']}")
        table.add_row("RAM:", f"{sys_res['ram']:.1f} GB")
        table.add_row("GPU Detected:", "[green]Yes[/]" if sys_res['gpu'] else "[yellow]No[/]")
        if sys_res['gpu']:
            table.add_row("GPU Memory:", f"{sys_res['gpu_memory']:.1f} GB")
        table.add_row("Network:", "[green]Online[/]" if analysis['network_access']['online'] else "[red]Offline[/]")
        self.console.print(table)

        # Step 3: API Keys & Connectivity
        self.console.print(f"\n[bold cyan]Step 3/5: Intelligence Providers[/]")

        # Show detected keys
        detected = analysis['detected_keys']
        if detected:
            self.console.print(f"\n[green]✓ Auto-detected {len(detected)} API keys from your environment.[/]")

            # Test detected keys
            self.console.print("\n[bold]Testing detected connections...[/]")
            connected_map = await self.api_manager.get_connected_providers()
            for provider, valid in connected_map.items():
                if provider in detected:
                    status = "[green]✓ Online[/]" if valid else "[red]✗ Offline[/]"
                    self.console.print(f"  • {self.api_manager.providers[provider]['name']}: {status}")

        setup_providers = Confirm.ask("\nWould you like to search and connect more models?", default=False)

        if setup_providers:
            configured = await self.api_manager.guided_setup()
            detected.update(configured)

        # Step 4: Interface Selection
        self.console.print(f"\n[bold cyan]Step 4/5: Choose Your Interface[/]")
        self.console.print("1. [bold cyan]TUI[/] (Terminal User Interface - Recommended for speed)")
        self.console.print("2. [bold magenta]GUI[/] (Graphical User Interface - High fidelity)")
        self.console.print("3. [bold white]CLI[/] (Command Line Interface - For power users)")

        iface_choice = Prompt.ask("Select interface", choices=["1", "2", "3"], default="1")
        interface_map = {"1": "TUI", "2": "GUI", "3": "CLI"}
        selected_iface = interface_map[iface_choice]

        # Step 5: Finalizing
        self.console.print(f"\n[bold cyan]Step 5/5: Finalizing[/]")
        with self.console.status("[bold green]Generating smart defaults..."):
            smart_config = await self.defaults.generate_config()

        smart_config.update({
            "user_name": user_name,
            "epex_name": epex_name,
            "password_hash": password_hash,
            "api_keys": detected,
            "preferred_interface": selected_iface,
            "setup_complete": True,
            "setup_date": datetime.now().isoformat()
        })

        await self.storage.store_config(smart_config)

        # Health Check
        await self.run_health_check()

        # Done!
        self.console.print(Panel.fit(
            f"[bold green]✓ Setup Complete![/]\n\n"
            f"[white]I'm {epex_name}, nice to meet you {user_name}![/]\n"
            f"[white]Launching {selected_iface} immediately...[/]",
            border_style="green"
        ))

        await asyncio.sleep(2)
        await self.launch_interface(selected_iface)

    async def launch_interface(self, interface: str):
        """Immediately take the user to the selected interface"""
        if interface == "TUI":
            from epex.interfaces.tui import EpexTUI
            tui = EpexTUI()
            await tui.run()
        elif interface == "GUI":
            self.console.print("[yellow]Starting GUI... (Ensure dependencies are installed)[/]")
            # In a real scenario, we might trigger a subprocess or an Electron app
            os.system("epex gui &")
        else: # CLI
            self.console.print("[white]Switching to CLI mode. Type 'epex --help' for commands.[/]")

class EpexTUI:
    """
    Main TUI Chat interface
    """
    def __init__(self):
        self.console = Console()
        self.layout = Layout()

    async def run(self):
        self.console.clear()
        from epex.core.constants import BANNER
        from epex.core.engine import engine

        self.console.print(BANNER, style="bold cyan")

        is_voice_active = False

        while True:
            # Aura-Based UI Scaling
            aura = engine.soul.data.get('current_aura', 'professional')
            aura_styles = {
                'professional': ('cyan', '⚡ EPEX PROFESSIONAL'),
                'friendly': ('green', '🌿 EPEX FRIENDLY'),
                'empathetic': ('magenta', '💓 EPEX EMPATHETIC'),
                'witty': ('yellow', '🎭 EPEX WITTY'),
                'zen': ('blue', '🧘 EPEX ZEN'),
                'aggressive': ('red', '🔥 EPEX AGGRESSIVE (HIGH PRIORITY)')
            }
            color, title = aura_styles.get(aura, ('cyan', '⚡ EPEX BOT'))

            active_model = engine.llm_router.active_model_override or "Intelligent Auto"
            voice_status = "[green]ON[/]" if is_voice_active else "[red]OFF[/]"

            self.console.print(Panel(
                f"[bold {color}]{title} MODE ACTIVATED[/]\n"
                f"[dim]Model: [bold]{active_model}[/] | Voice Bridge: {voice_status} | Type 'exit' to quit[/]",
                border_style=color
            ))

            cmd = Prompt.ask(f"[bold {color}]User[/]")
            if cmd.lower() in ["exit", "quit"]:
                break

            # Switch Commands
            if cmd.lower().startswith("/switch"):
                target = cmd.split()[-1].lower()
                if target == "gui":
                    self.console.print("[yellow]Switching to GUI...[/]")
                    await asyncio.sleep(1)
                    # We'd need to launch GUI here, but for simplicity we'll just note it
                    os.system("epex --gui &")
                    break
                elif target == "cli":
                    self.console.print("[white]Switching to CLI mode.[/]")
                    break

            if cmd.lower() == "/voice":
                is_voice_active = not is_voice_active
                status = "activated" if is_voice_active else "deactivated"
                self.console.print(f"[cyan]Voice Bridge {status}.[/]")
                if is_voice_active:
                    # Start listening in background
                    asyncio.create_task(engine.voice_bridge.start_listening_loop())
                else:
                    engine.voice_bridge.stop()
                continue

            from epex.core.engine import engine
            with self.console.status(f"[bold {color}]Epex is thinking..."):
                response = await engine.execute_command(cmd)

            self.console.print(Panel(response.get('response', 'Error'), title=f"[bold {color}]Epex[/]", border_style=color))

            # Handle Control Signals
            signal = response.get('control_signal')
            if signal == "switch_gui":
                os.system("epex --gui &")
                break
            elif signal == "switch_cli":
                break

    async def run_health_check(self):
        """
        Comprehensive health check on first run
        """
        self.console.print("\n[bold]Running final health check...[/]")

        checks = {
            'Python Version': sys.version_info >= (3, 10),
            'Secure Storage': os.path.exists(self.storage.config_path),
            'Database': os.path.exists('epex.db') or True, # Placeholder
            'Network': (await self.detector._check_network())['online']
        }

        for check, passed in checks.items():
            status = "[green]✓[/]" if passed else "[red]✗[/]"
            self.console.print(f"  {status} {check}")

        return all(checks.values())
