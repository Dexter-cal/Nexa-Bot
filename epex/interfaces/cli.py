import sys
import asyncio
import argparse
import os
import time
import json
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from epex.interfaces.tui import TUISetupWizard
from epex.core.engine import engine

console = Console()

class NexaCLI:
    """Enhanced EPEX Command Line Interface with Tab Completion and Tool Mapping"""

    def __init__(self):
        self.commands = [
            'help', 'status', 'keys', 'agents', 'spawn-swarm',
            'spawn-agents', 'privacy-scan', 'disk', 'backup',
            'teach', 'play', '/mode', '/role', '/cost', 'exit', 'quit',
            '/switch', '/model', 'clear', 'discover', 'peers'
        ]
        self.setup_completion()

    def setup_completion(self):
        """Setup tab completion using readline"""
        try:
            import readline
            readline.set_completer(self.complete)
            readline.parse_and_bind('tab: complete')

            history_file = os.path.expanduser('~/.epex/history')
            if os.path.exists(history_file):
                readline.read_history_file(history_file)

            import atexit
            atexit.register(readline.write_history_file, history_file)
        except:
            pass

    def complete(self, text, state):
        matches = [cmd for cmd in self.commands if cmd.startswith(text)]
        return matches[state] if state < len(matches) else None

    async def execute_cli_command(self, command: str):
        parts = command.strip().split()
        if not parts: return

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == 'help':
            self.show_help()
        elif cmd == 'status' or cmd == '/status':
            from epex.core.engine import engine
            await engine.system_context.refresh()
            summary = engine.system_context.get_summary()
            console.print(Panel(summary, title="SYSTEM STATUS", border_style="cyan"))
        elif cmd == 'clear':
            console.clear()
        elif cmd == 'disk':
            await self.handle_disk(args)
        elif cmd == 'keys':
            await self.handle_keys(args)
        elif cmd == 'backup':
            await self.handle_backup(args)
        elif cmd == 'agents' or cmd == 'spawn-agents':
            await self.handle_agents(args)
        elif cmd == 'spawn-swarm':
            await self.handle_swarm(args)
        elif cmd == 'teach':
            await self.handle_teach(args)
        elif cmd == 'play':
            await self.handle_play(args)
        elif cmd == 'privacy-scan':
            await self.handle_privacy_scan()
        elif cmd == 'discover':
            await self.handle_discovery()
        elif cmd == 'peers':
            await self.handle_peers(args)
        elif cmd == '/cost':
            stats = engine.llm_router.usage_tracker.get_today_stats()
            console.print(Panel(f"💰 **Total Cost Today**: ${stats['total_cost']:.4f}\n📊 **Tokens Used**: {stats['total_tokens']}", title="USAGE STATS", border_style="green"))
        elif cmd == '/switch':
            if args:
                target = args[0].lower()
                if target == 'gui': await launch_gui()
                elif target == 'tui':
                    from epex.interfaces.textual_tui import EpexTextualApp
                    app = EpexTextualApp()
                    app.run()
        elif cmd == '/model':
            if len(args) > 0:
                if args[0] == 'search' and len(args) > 1:
                    await self.handle_model_search(args[1])
                else:
                    engine.llm_router.active_model_override = args[0]
                    console.print(f"[green]✓ Active model set to: {args[0]}[/]")
        elif cmd == '/mode':
            if args:
                res = await engine.execute_command(f"set mode to {args[0]}")
                console.print(f"[green]✓ {res.get('response')}[/]")
        elif cmd == '/role':
            if args:
                res = await engine.execute_command(f"set role to {args[0]}")
                console.print(f"[purple]✓ {res.get('response')}[/]")
        elif cmd == 'exit' or cmd == 'quit':
            sys.exit(0)
        else:
            # Pass to general AI execution
            await self.process_ai_query(command)

    async def handle_keys(self, args):
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        manager = UniversalAPIKeyManager()

        if not args or args[0] == 'list':
            table = Table(title="🔑 CONNECTED API PROVIDERS", border_style="cyan")
            table.add_column("Provider", style="bold cyan")
            table.add_column("Status", style="lime")
            table.add_column("Details", style="dim")

            status_map = await manager.get_connected_providers()
            config = await manager.vault.load_config()
            discovered = config.get('discovered_models', {})

            for p, online in status_map.items():
                symbol = "[green]●[/]" if online else "[red]○[/]"
                model_count = len(discovered.get(p, []))
                table.add_row(p.capitalize(), f"{symbol} {'Online' if online else 'Offline'}", f"{model_count} models discovered")

            console.print(table)
            console.print("\n[dim]Use 'epex' launcher (option 4) to add or remove keys.[/dim]")
        elif args[0] == 'add':
             # For CLI simplicity, we just redirect to launcher logic or prompt here
             if len(args) >= 3:
                  await set_api_key(args[1], args[2])
             else:
                  console.print("[red]Usage: keys add <provider> <key>[/red]")

    async def handle_disk(self, args):
        sub = args[0] if args else 'health'
        if sub == 'health':
            res = await engine.execute_command("Run maint.disk_health")
            console.print(Panel(str(res.get('response')), title="DISK HEALTH", border_style="blue"))
        elif sub == 'analyze':
            res = await engine.execute_command("Run maint.analyze_usage")
            console.print(Panel(str(res.get('response')), title="DISK ANALYSIS", border_style="blue"))
        elif sub == 'clean':
            res = await engine.execute_command("Run maint.cleanup")
            console.print(Panel(str(res.get('response')), title="DISK CLEANUP", border_style="green"))

    async def handle_backup(self, args):
        path = args[0] if args else "."
        with Progress(SpinnerColumn(), TextColumn("[cyan]Backing up {task.fields[path]}..."), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%")) as progress:
            task = progress.add_task("backup", total=100, path=path)
            res = await engine.execute_command(f"Run system.backup path={path}")
            for _ in range(10):
                time.sleep(0.1)
                progress.update(task, advance=10)
        console.print(f"[green]✓ Backup complete: {res.get('response')}[/]")

    async def handle_agents(self, args):
        res = await engine.execute_command("list agents")
        console.print(Panel(str(res.get('response')), title="ACTIVE AGENTS", border_style="lime"))

    async def handle_swarm(self, args):
        goal = " ".join(args)
        console.print(f"[cyan]⚡ Spawning swarm for goal: {goal}[/]")
        res = await engine.execute_command(f"spawn swarm for {goal}")
        console.print(f"[green]{res.get('response')}[/]")

    async def handle_teach(self, args):
        name = args[0] if args else "workflow"
        res = await engine.execute_command(f"Run automation.teach name={name}")
        console.print(f"[yellow]📹 {res.get('response')}[/]")
        console.print("[dim]Press Ctrl+C to stop recording (simulated)[/]")
        try:
            while True: await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print(f"\n[green]✓ Workflow '{name}' recorded successfully.[/]")

    async def handle_play(self, args):
        name = args[0] if args else "workflow"
        with console.status(f"[cyan]Replaying workflow '{name}'..."):
            res = await engine.execute_command(f"Run automation.play name={name}")
        console.print(f"[green]▶️ {res.get('response')}[/]")

    async def handle_peers(self, args):
        from epex.core.networking import NetworkingManager
        net = NetworkingManager()

        if not args or args[0] == 'list':
            await net.list_peers()
        elif args[0] == 'connect':
            if len(args) >= 3:
                name = args[1]
                url = args[2]
                key = args[3] if len(args) > 3 else None
                await net.connect_to_peer(name, url, key)
            else:
                console.print("[red]Usage: peers connect <name> <url> [api_key][/red]")
        elif args[0] == 'delegate':
            if len(args) >= 3:
                peer = args[1]
                cmd = " ".join(args[2:])
                res = await net.delegate(peer, cmd)
                if res:
                    console.print(f"\n[bold cyan]{peer} says:[/]\n{res.get('response')}")
            else:
                console.print("[red]Usage: peers delegate <peer_name> <command>[/red]")

    async def handle_discovery(self):
        from epex.intelligence.discovery import ModelDiscoverySystem
        discovery = ModelDiscoverySystem()
        with console.status("[bold yellow]Scanning HuggingFace for trending models..."):
            await discovery.run_discovery()

        pending = await discovery.get_pending_report()
        if not any(pending.values()):
            console.print("[green]No new models discovered.[/]")
            return

        for cat, models in pending.items():
            if models:
                table = Table(title=f"🆕 {cat.upper()} MODELS DISCOVERED")
                table.add_column("Model ID", style="cyan")
                table.add_column("Downloads", style="green")
                for m in models[:10]:
                    table.add_row(m['id'], f"{m['downloads']:,}")
                console.print(table)

        console.print("\n[dim]Run 'epex' launcher to review and approve these models.[/]")

    async def handle_model_search(self, query):
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        manager = UniversalAPIKeyManager()
        with console.status(f"[bold yellow]Searching HuggingFace for '{query}'..."):
             results = await manager.search_huggingface(query)

        if results:
            table = Table(title=f"HF Models Matching: {query}")
            table.add_column("Model ID", style="cyan")
            table.add_column("Capabilities")
            for m in results:
                table.add_row(m['id'], ", ".join(m['capabilities']))
            console.print(table)
        else:
            console.print("[red]No models found.[/]")

    async def handle_privacy_scan(self):
        with console.status("[red]Running Deep Privacy Scan..."):
            res = await engine.execute_command("Run privacy.guardian_scan")
        console.print(Panel(str(res.get('response')), title="🛡️ PRIVACY REPORT", border_style="red"))

    async def process_ai_query(self, query: str):
        from epex.foundation.storage import SecureConfigStorage
        storage = SecureConfigStorage()
        config = await storage.load_config()
        epex_name = config.get('epex_name', 'Epex')

        with console.status("[bold sky_blue1]Thinking..."):
            result = await engine.execute_command(query)

        if result['success']:
            model_str = result.get('model', 'unknown')
            latency = result.get('latency', 0)
            cost = result.get('cost', 0)

            badge = f"[bold cyan]🤖 {model_str}[/] • [dim]{latency:.1f}s[/] • [bold green]${cost:.4f}[/]"
            console.print(Panel(badge, border_style="dim", expand=False))

            thoughts = result.get('thoughts', [])
            if thoughts:
                console.print(Panel("\n".join([f"💭 {t}" for t in thoughts]), title="REASONING", border_style="dim", width=100))

            console.print(f"\n[bold sky_blue1]{epex_name} >[/]")
            console.print(Markdown(result['response']))

            if result.get('switched'):
                console.print(Panel(f"[yellow]🔄 Switched: {result.get('switch_reason')}[/]", border_style="yellow", expand=False))

            # Smart Suggestions
            self.suggest_next_command(query)
        else:
            console.print(f"[bold red]Error:[/] {result.get('error')}")

    def suggest_next_command(self, last_command: str):
        """Suggest what to do next based on the last command"""
        cmd_low = last_command.lower()
        suggestions = {
            'spawn-swarm': "Try 'agents' to see them in action",
            'privacy-scan': "View full logs with 'status' or check /cost",
            'backup': "Verify your backup integrity with 'disk analyze'",
            'teach': "Replay your workflow anytime with 'play'",
            'disk': "Use 'disk clean' to free up space identified in analysis"
        }

        for key, suggestion in suggestions.items():
            if key in cmd_low:
                console.print(f"\n[dim]💡 Pro-Tip: {suggestion}[/dim]")
                break

    def show_help(self):
        help_text = """
[bold cyan]EPEX CLI COMMANDS[/bold cyan]

[bold]System Commands:[/bold]
  [cyan]status[/cyan]         Full system health and connectivity report
  [cyan]keys list[/cyan]      Show connected API providers and model counts
  [cyan]clear[/cyan]          Clear terminal screen
  [cyan]/cost[/cyan]          Display today's API usage and cost
  [cyan]/switch [tui|gui][/cyan] Switch interface

[bold]Maintenance:[/bold]
  [cyan]disk health[/cyan]    Check SMART status of drives
  [cyan]disk analyze[/cyan]   Find large files and junk
  [cyan]disk clean[/cyan]     Clear temp files and cache
  [cyan]backup [path][/cyan]  Create a compressed backup

[bold]Agents & Swarms:[/bold]
  [cyan]agents[/cyan]         List all active sub-agents
  [cyan]spawn-swarm [goal][/cyan] Launch a parallel agent swarm
  [cyan]spawn-agents [role][/cyan] Spawn specific specialized agents

[bold]Networking:[/bold]
  [cyan]peers list[/cyan]       List all connected EPEX peers
  [cyan]peers connect[/cyan]    Connect to a new EPEX instance
  [cyan]peers delegate[/cyan]   Send a command to a specific peer

[bold]Automation:[/bold]
  [cyan]teach [name][/cyan]   Record a new macro/workflow
  [cyan]play [name][/cyan]    Replay a recorded workflow

[bold]Intelligence:[/bold]
  [cyan]discover[/cyan]       Scan HuggingFace for trending models
  [cyan]/model search [q][/cyan] Search for models on HuggingFace
  [cyan]/model [id][/cyan]      Manually override active model

[bold]General:[/bold]
  Just type your question or task in natural language.
"""
        console.print(Panel(help_text, title="HELP", border_style="cyan"))

async def async_main():
    parser = argparse.ArgumentParser(description="Epex Bot CLI")
    parser.add_argument("prompt", nargs="?", help="Prompt for Epex Bot")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    parser.add_argument("--mode", help="Set operational mode")
    parser.add_argument("--role", help="Set agent role")
    parser.add_argument("--spawn", help="Spawn a specialized agent with role")
    parser.add_argument("--chat", action="store_true", help="Start interactive neural chat")
    parser.add_argument("--visuals", action="store_true", help="Display visual mockups of Epex interfaces")
    parser.add_argument("--quick-setup", action="store_true", help="Fast-track setup with automatic defaults")
    parser.add_argument("--key", nargs=2, metavar=('PROVIDER', 'VALUE'), help="Quickly set an API key (e.g. --key openai sk-...)")
    parser.add_argument("--connect", nargs=3, metavar=('NAME', 'URL', 'KEY'), help="Connect to another Epex instance")
    parser.add_argument("--peers", action="store_true", help="List all connected Epex peers")
    parser.add_argument("--voice", action="store_true", help="Activate hands-free voice command bridge")
    parser.add_argument("--tool-hub", action="store_true", help="Open the EPEX Tool Hub")
    parser.add_argument("--gui", action="store_true", help="Launch the EPEX Web-Based GUI")
    parser.add_argument("--discover", action="store_true", help="Scan HuggingFace for trending models")

    args = parser.parse_args()

    if args.setup:
        wizard = TUISetupWizard()
        await wizard.run()
    elif args.quick_setup:
        await run_quick_setup()
    elif args.key:
        await set_api_key(args.key[0], args.key[1])
    elif args.connect:
        from epex.core.network_node import network_node
        await network_node.add_peer(args.connect[0], args.connect[1], args.connect[2])
        print(f"✓ Successfully connected to peer '{args.connect[0]}'")
    elif args.peers:
        from epex.core.network_node import network_node
        await network_node.load_peers()
        if not network_node.peers:
            print("No peers connected.")
        else:
            print("\nConnected Epex Peers:")
            for p in network_node.peers:
                print(f" • {p['name']} ({p['url']}) - Status: {p['status']}")
    elif args.voice:
        print("🎙️ Activating Voice Command Bridge... (Say 'Epex' to trigger)")
        await engine.start()
        await engine.voice_bridge.start_listening_loop()
    elif args.tool_hub:
        from epex.interfaces.tool_hub import ToolHub
        hub = ToolHub()
        await hub.run()
    elif args.gui:
        await launch_gui()
    elif args.discover:
        cli = NexaCLI()
        await cli.handle_discovery()
    elif args.visuals:
        from epex.tools.visualizer import GenerateMockupsTool
        tool = GenerateMockupsTool()
        result = await tool.execute()
        print(result.output)
    elif args.chat or (not args.prompt and len(sys.argv) == 1 and not args.spawn and not args.visuals):
        cli = NexaCLI()
        await start_chat_loop(cli)
    elif args.spawn:
        result = await engine.execute_command(f"spawn {args.spawn} agent")
        print(f"\n{result.get('message', 'Spawning...')}")
    elif args.prompt:
        result = await engine.execute_command(args.prompt)
        if result['success']:
            print(f"\n{result['response']}")
            if result.get('switched'):
                print(f"\n[Note: Switched from {result['from_model']} to {result['model']} because: {result['switch_reason']}]")
        else:
            print(f"Error: {result.get('reason', 'Unknown error')}")

async def start_chat_loop(cli: NexaCLI = None):
    from rich.console import Console
    from rich.panel import Panel
    from epex.foundation.storage import SecureConfigStorage

    if not cli: cli = NexaCLI()
    storage = SecureConfigStorage()
    config = await storage.load_config()
    user_name = config.get('user_name', 'User')
    epex_name = config.get('epex_name', 'Epex')

    from epex.core.constants import BANNER
    console.print(BANNER, style="bold cyan")
    console.print(Panel(f"[bold sky_blue1]Neural Chat Interface Initialized[/]\n[italic text_slate_500]{epex_name.upper()} BOT is ready. Type 'help' for commands or 'exit' to quit.[/]", border_style="sky_blue1"))

    while True:
        try:
            user_input = console.input(f"\n[bold sky_blue1]{user_name} > [/]")
            if not user_input.strip(): continue

            # Use CLI executor for unified command handling
            await cli.execute_cli_command(user_input)

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"\n[bold red]System Error:[/] {e}")

async def set_api_key(provider: str, value: str):
    from rich.console import Console
    from epex.foundation.storage import SecureConfigStorage
    console = Console()
    storage = SecureConfigStorage()
    config = await storage.load_config()
    if 'api_keys' not in config: config['api_keys'] = {}
    config['api_keys'][provider.lower()] = value
    await storage.store_config(config)
    console.print(f"[bold green]✓ API Key for '{provider}' has been saved securely.[/]")

async def run_quick_setup():
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from epex.intelligence.api_manager import UniversalAPIKeyManager
    from epex.foundation.storage import SecureConfigStorage
    from epex.intelligence.defaults import SmartDefaultsEngine

    console = Console()
    console.clear()
    console.print(Panel("[bold green]⚡ EPEX EXPRESS SETUP[/]\n[white]Let's get you online in 30 seconds.[/]", border_style="green"))

    user_name = Prompt.ask("Your name", default="Max")
    bot_name = Prompt.ask("Bot name", default="Bill")

    # Quick API key entry
    console.print("\n[bold cyan]API Keys (Optional - press Enter to skip)[/]")
    openai_key = Prompt.ask("OpenAI Key", password=True, default="")
    google_key = Prompt.ask("Google/Gemini Key", password=True, default="")

    storage = SecureConfigStorage()
    defaults = SmartDefaultsEngine()

    config = await defaults.generate_config()
    config.update({
        "user_name": user_name,
        "epex_name": bot_name,
        "api_keys": {}
    })

    if openai_key: config['api_keys']['openai'] = openai_key
    if google_key: config['api_keys']['google'] = google_key

    await storage.store_config(config)

    console.print(Panel.fit(f"[bold green]✓ Express Setup Complete![/]\n[white]Welcome, {user_name}. I am {bot_name}.[/]\nRun: [bold]epex chat[/]", border_style="green"))

async def launch_gui():
    import uvicorn
    import webbrowser
    from rich.console import Console
    console = Console()
    console.print("[bold cyan]🚀 Launching EPEX APEX GUI...[/]")
    console.print("[dim]Starting local server at http://127.0.0.1:8000[/]")

    # Auto-open browser after a short delay
    async def open_browser():
        await asyncio.sleep(2)
        webbrowser.open("http://127.0.0.1:8000")

    asyncio.create_task(open_browser())

    config = uvicorn.Config("epex.api.app:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
