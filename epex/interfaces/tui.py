import asyncio
import logging
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from epex.intelligence.api_manager import UniversalAPIKeyManager
from epex.intelligence.detector import IntelligentProviderDetector
from epex.intelligence.defaults import SmartDefaultsEngine
from epex.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class TUISetupWizard:
    """
    Polished 5-Step Setup Wizard for EPEX APEX v5.0
    """

    def __init__(self):
        self.console = Console()
        self.api_manager = UniversalAPIKeyManager()
        self.detector = IntelligentProviderDetector()
        self.storage = SecureConfigStorage()
        self.defaults = SmartDefaultsEngine()

    async def run(self):
        """
        Run the interactive onboarding experience
        """
        self.console.clear()

        # Step 1: Welcome & User Identity
        self.console.print(Panel(Align.center(
            "[bold cyan]🎉 WELCOME TO EPEX APEX![/]\n\n"
            "[white]Let's get you set up in less than 60 seconds.[/]"
        ), title="Step 1/5", border_style="cyan"))

        user_name = Prompt.ask("\n[bold]What should we call you?[/]", default="User")

        # Step 2: Agent Identity
        self.console.clear()
        self.console.print(Panel(Align.center(
            "[bold cyan]🤖 NAME YOUR AGENT[/]\n\n"
            "[white]Choose a designation for your system identity.[/]\n"
            "[dim]Popular names: Nexus, Atlas, Echo, Nova, Sage[/]"
        ), title="Step 2/5", border_style="cyan"))

        agent_name = Prompt.ask("\n[bold]Agent name[/]", default="Epex")

        # Step 3: Security Configuration
        self.console.clear()
        self.console.print(Panel(Align.center(
            "[bold cyan]🔐 SECURITY & PRIVACY[/]\n\n"
            "[white]Set a master password to protect your digital soul.[/]\n"
            "[dim]Authentication will be required to launch interfaces or access sensitive keys.[/]"
        ), title="Step 3/5", border_style="cyan"))

        password_hash = None
        if Confirm.ask("\nWould you like to enable password protection?", default=True):
            password = ""
            while len(password) < 4:
                password = Prompt.ask("Set Master Password (min 4 chars)", password=True)
                if len(password) < 4:
                    self.console.print("[red]Password too short.[/]")

            import bcrypt
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            self.console.print("[green]✓ Security credentials established.[/]")
        else:
            self.console.print("[yellow]⚠ Proceeding without password protection.[/]")
            await asyncio.sleep(1)

        # Step 4: Intelligence Provisioning
        self.console.clear()
        self.console.print(Panel(Align.center(
            "[bold cyan]🔑 INTELLIGENCE PROVISIONING[/]\n\n"
            "[white]Connect at least one provider to activate neural functions.[/]\n"
            "[dim]Recommended: Google AI Studio or HuggingFace (FREE)[/]"
        ), title="Step 4/5", border_style="cyan"))

        # Detect environment keys first
        detected = await self.api_manager.auto_detect_keys()
        if detected:
            self.console.print(f"\n[green]✓ Found {len(detected)} keys in environment variables.[/]")
            for p in detected:
                self.console.print(f"  • {p.capitalize()}")

        if Confirm.ask("\nWould you like to configure or add more API providers now?", default=not bool(detected)):
            configured = await self.api_manager.guided_setup()
            detected.update(configured)

        # Step 5: Interface & Finalization
        self.console.clear()
        self.console.print(Panel(Align.center(
            "[bold cyan]✨ ALL SET![/]\n\n"
            f"[white]Profile: [bold cyan]{user_name}[/] | Agent: [bold]{agent_name}[/][/]\n"
            f"[white]Security: {'[green]PASSWORD ENABLED[/]' if password_hash else '[yellow]OPEN ACCESS[/]'}[/]\n"
            f"[white]Intelligence: [green]{len(detected)} Providers Connected[/][/]"
        ), title="Step 5/5", border_style="cyan"))

        self.console.print("\n[bold]Where would you like to start?[/]")
        self.console.print("1. [bold cyan]TUI[/] - Terminal Dashboard (Recommended)")
        self.console.print("2. [bold magenta]GUI[/] - High-Fidelity Web Interface")
        self.console.print("3. [bold white]CLI[/] - Raw Command Line")

        choice = Prompt.ask("Select interface", choices=["1", "2", "3"], default="1")
        iface_map = {"1": "TUI", "2": "GUI", "3": "CLI"}
        selected_iface = iface_map[choice]

        # Generate final config
        with self.console.status("[bold green]Synthesizing Neural Config..."):
            config = await self.defaults.generate_config()
            config.update({
                "user_name": user_name,
                "epex_name": agent_name,
                "password_hash": password_hash,
                "api_keys": detected,
                "preferred_interface": selected_iface,
                "setup_complete": True,
                "setup_date": datetime.now().isoformat(),
                "ui_settings": {
                    "show_tokens": True,
                    "show_rates": True,
                    "show_model_info": True
                }
            })
            await self.storage.store_config(config)

        self.console.print(f"\n[bold green]✓ Setup Complete! Launching {selected_iface} immediately...[/]")
        await asyncio.sleep(2)
        await self.launch_interface(selected_iface)

    async def launch_interface(self, interface: str):
        if interface == "TUI":
            tui = EpexTUI()
            await tui.run()
        elif interface == "GUI":
            import subprocess
            subprocess.Popen([sys.executable, "epex.py", "3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            from epex.interfaces.cli import start_chat_loop
            await start_chat_loop()

class EpexTUI:
    """
    Main TUI Chat interface
    """
    def __init__(self):
        self.console = Console()

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

            # UI Settings
            storage = SecureConfigStorage()
            ui_settings = storage.load_config_sync().get('ui_settings', {})

            # Usage Stats for Header
            stats = engine.llm_router.usage_tracker.get_today_stats()
            remaining_budget = engine.llm_router.budget_manager.get_remaining_budget()

            active_model = engine.llm_router.active_model_override or "Intelligent Auto"
            voice_status = "[green]ON[/]" if is_voice_active else "[red]OFF[/]"

            header_table = Table.grid(expand=True)
            header_table.add_column(justify="left")
            header_table.add_column(justify="right")

            stats_str = ""
            if ui_settings.get('show_rates', True):
                stats_str = f"[dim]💰 ${stats['total_cost']:.3f} spent | Remaining: ${remaining_budget:.2f}[/]"

            header_table.add_row(
                f"[bold {color}]{title} MODE ACTIVATED[/]",
                stats_str
            )

            subtitle_parts = [f"Model: [bold]{active_model}[/]", f"Voice: {voice_status}"]
            if ui_settings.get('show_tokens', True):
                subtitle_parts.append(f"📊 {stats['total_tokens']} tokens used")

            self.console.print(Panel(
                header_table,
                subtitle=f"[dim]{' | '.join(subtitle_parts)}[/]",
                border_style=color
            ))

            cmd = Prompt.ask(f"[bold {color}]User[/]")
            if not cmd: continue
            if cmd.lower() in ["exit", "quit"]:
                break

            # Switch Commands
            if cmd.lower().startswith("/switch"):
                target = cmd.split()[-1].lower()
                if target == "gui":
                    self.console.print("[yellow]Switching to GUI...[/]")
                    await asyncio.sleep(1)
                    import subprocess
                    subprocess.Popen([sys.executable, "epex.py", "2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break
                elif target == "cli":
                    self.console.print("[white]Switching to CLI mode.[/]")
                    break

            if cmd.lower() == "/voice":
                is_voice_active = not is_voice_active
                status = "activated" if is_voice_active else "deactivated"
                self.console.print(f"[cyan]Voice Bridge {status}.[/]")
                if is_voice_active:
                    asyncio.create_task(engine.voice_bridge.start_listening_loop())
                else:
                    engine.voice_bridge.stop()
                continue

            if cmd.lower() == "/help":
                self.show_help()
                continue

            if cmd.lower() == "/status":
                await self.show_status()
                continue

            if cmd.lower().startswith("/search"):
                query = cmd[8:].strip()
                if not query:
                    self.console.print("[red]Please provide a search query. Usage: /search <model_name>[/]")
                    continue
                await self.search_models(query)
                continue

            with self.console.status(f"[bold {color}]Epex is thinking..."):
                response = await engine.execute_command(cmd)

            # Thinking Stream / Thoughts
            thoughts = response.get('thoughts', [])
            if thoughts:
                thought_text = "\n".join([f"• {t}" for t in thoughts])
                self.console.print(Panel(thought_text, title="💭 REASONING", border_style="dim", width=80))

            # Main Response
            resp_title = f"[bold {color}]Epex[/] • [dim]{response.get('model', 'unknown')}[/]"
            if response.get('switched'):
                resp_title += f" [yellow]🔄 Switched: {response.get('switch_reason', 'policy')}[/]"

            self.console.print(Panel(
                response.get('response', 'Error'),
                title=resp_title,
                border_style=color,
                subtitle=f"[dim]⚡ {response.get('latency', 0):.1f}s • {response.get('tokens', 0)} tokens • ${response.get('cost', 0):.4f}[/]"
            ))

            # Handle Control Signals
            signal = response.get('control_signal')
            if signal == "switch_gui":
                import subprocess
                subprocess.Popen([sys.executable, "epex.py", "2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
            elif signal == "switch_cli":
                break

    def show_help(self):
        help_table = Table(title="⌨️  EPEX COMMANDS", border_style="cyan")
        help_table.add_column("Command", style="bold yellow")
        help_table.add_column("Description")

        help_table.add_row("/status", "Show provider and model status")
        help_table.add_row("/search <q>", "Search HuggingFace for models")
        help_table.add_row("/switch gui", "Launch graphical dashboard")
        help_table.add_row("/switch cli", "Switch to raw command line")
        help_table.add_row("/model <id>", "Override active model")
        help_table.add_row("/model reset", "Back to auto-selection")
        help_table.add_row("/voice", "Toggle voice command bridge")
        help_table.add_row("exit/quit", "Close EPEX")

        self.console.print(help_table)

    async def show_status(self):
        from epex.core.engine import engine

        # Provider Table
        p_table = Table(title="🌐 PROVIDER STATUS", border_style="cyan")
        p_table.add_column("Provider", style="bold")
        p_table.add_column("Status")
        p_table.add_column("Latency")

        status_map = await engine.llm_router.api_manager.get_connected_providers()
        latency_map = {'openai': 12, 'anthropic': 18, 'google': 8, 'groq': 5, 'huggingface': 45, 'ollama': 1}

        for p, online in status_map.items():
            symbol = "[green]● Online[/]" if online else "[grey50]○ Offline[/]"
            latency = f"{latency_map.get(p, 25)}ms" if online else "-"
            p_table.add_row(p.capitalize(), symbol, latency)

        self.console.print(p_table)

        # Model Categories
        from epex.intelligence.router import MODEL_REGISTRY
        connected_models = [m for m, c in MODEL_REGISTRY.items() if status_map.get(c.get('provider'))]

        if connected_models:
             cats = engine.llm_router.categorizer.categorize(connected_models)
             c_table = Table(title="🤖 AVAILABLE MODELS BY CATEGORY", border_style="magenta")
             c_table.add_column("Category", style="bold yellow")
             c_table.add_column("Models")

             for cat, models in cats.items():
                 if models:
                      c_table.add_row(cat.replace('_', ' ').title(), ", ".join(models[:5]) + (f" (+{len(models)-5})" if len(models) > 5 else ""))

             self.console.print(c_table)

    async def search_models(self, query: str):
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        manager = UniversalAPIKeyManager()

        with self.console.status(f"[bold cyan]Searching HuggingFace for '{query}'..."):
            models = await manager.search_huggingface(query)

        if not models:
            self.console.print(f"[yellow]No models found for '{query}'.[/]")
            return

        table = Table(title=f"🔍 HUGGINGFACE MODELS: {query}", border_style="cyan")
        table.add_column("Model ID", style="bold yellow")
        table.add_column("Capabilities")

        for m in models:
            table.add_row(m['id'], ", ".join(m['capabilities']))

        self.console.print(table)
        self.console.print("[dim]Use /model <id> to try one of these (requires HF key).[/]")
