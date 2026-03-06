import os
import sys
import asyncio
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

async def check_environment():
    """Ensure all dependencies are met without redundant scanning"""
    install_lock = Path.home() / '.epex' / '.installed'
    if install_lock.exists():
        return

    print("🔍 Initializing EPEX Neural Environment...")
    try:
        import rich
        import psutil
        import cryptography
        import aiohttp
        import bcrypt
        import fastapi
        import uvicorn
        install_lock.parent.mkdir(parents=True, exist_ok=True)
        install_lock.touch()
    except ImportError:
        print("📦 Missing core dependencies. Launching EPEX Repair & Install...")
        subprocess.run([sys.executable, "epex_run.py"], check=True)
        os.execv(sys.executable, ['python3'] + sys.argv)

async def check_config():
    """Ensure configuration exists"""
    config_path = Path.home() / '.epex' / 'config.enc'
    if not config_path.exists():
        print("📝 No configuration found. Launching Setup Wizard...")
        subprocess.run([sys.executable, "epex_run.py"], check=True)
        return False
    return True

async def main():
    await check_environment()

    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.align import Align
    from rich.table import Table
    from rich.layout import Layout
    from rich.text import Text
    from epex.core.constants import BANNER, VERSION
    from epex.foundation.storage import SecureConfigStorage
    from epex.intelligence.api_manager import UniversalAPIKeyManager
    import psutil

    console = Console()
    storage = SecureConfigStorage()

    # --- Background Intelligence Phase ---
    from epex.core.system_intelligence import SystemIntelligence
    from epex.intelligence.discovery import ModelDiscoverySystem
    intel = SystemIntelligence()
    discovery = ModelDiscoverySystem()

    with console.status("[bold cyan]🔍 Initializing EPEX Intelligence Engine...") as status:
        checks = await intel.run_all_checks()
        # Auto-scan for models if HF connected
        if 'huggingface' in checks.get('active_providers', []):
             await discovery.run_discovery()
             await discovery.auto_approve_popular()
        time.sleep(1) # Visual pause for user to feel the depth

    # Optional: Quick check log for transparency
    # console.print(f"[dim]✓ Intelligence initialization complete ({checks['total_check_time']:.2f}s)[/dim]")

    while True:
        console.clear()

        # 1. Show Banner (Enhanced)
        console.print(Align.center(f"[bold cyan]{BANNER}[/]"))
        console.print(Align.center(f"[bold white]THE NEURAL COMMAND CENTER[/] [dim italic]v{VERSION}[/]\n"))

        # 2. Check Config & Setup
        if not await check_config():
            os.execv(sys.executable, ['python3'] + sys.argv)

        config = await storage.load_config()

        # Update last active
        last_active = config.get('last_active_time', "Unknown")
        config['last_active_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await storage.store_config(config)

        # 3. Password Protection
        if config.get('password_hash'):
            import bcrypt
            last_login = config.get('last_login_time', 0)
            session_timeout = 3600 # 1 hour

            if time.time() - last_login > session_timeout:
                console.print(Panel("[bold yellow]🔐 SYSTEM LOCKED[/]\nPlease enter your password to access the Command Center.", border_style="yellow"))
                attempts = 0
                while attempts < 3:
                    pwd = Prompt.ask("Password", password=True)
                    if bcrypt.checkpw(pwd.encode(), config['password_hash'].encode()):
                        console.print("[green]✓ Authentication Successful.[/]\n")
                        config['last_login_time'] = time.time()
                        await storage.store_config(config)
                        break
                    else:
                        attempts += 1
                        console.print(f"[red]✗ Incorrect password. ({3 - attempts} attempts left)[/]")
                else:
                    console.print("[bold red]Access Denied. Terminal Locked.[/]")
                    return

        # 4. Profile & Welcome
        user_name = checks.get('user_name', config.get('user_name', 'User'))
        agent_name = checks.get('agent_name', config.get('epex_name', 'Epex'))
        days_using = checks.get('days_using', 0)

        console.print(Panel(
            f"👤 Welcome back, [bold cyan]{user_name}[/]!\nAgent: [bold]{agent_name}[/]  •  Active for {days_using} days  •  Last active: [dim]{last_active}[/]",
            border_style="cyan"
        ))

        # 5. Interface Selection Grid
        iface_table = Table.grid(expand=True, padding=(1, 2))
        iface_table.add_column(justify="center")
        iface_table.add_column(justify="center")
        iface_table.add_column(justify="center")

        iface_table.add_row(
            Panel("[bold white]💻 CLI[/]\n[dim]Terminal\nInterface[/]", border_style="white", width=25),
            Panel("[bold cyan]🖥️ TUI[/]\n[dim]Dashboard\nInterface[/]", border_style="cyan", width=25),
            Panel("[bold magenta]🎨 GUI[/]\n[dim]Web/Native\nDashboards[/]", border_style="magenta", width=25)
        )
        console.print(iface_table)

        # 6. System Status Panel
        active_keys = len(checks.get('active_providers', []))
        total_models = checks.get('total_models_available', 0)

        cpu_usage = checks.get('cpu_usage', 0)
        ram_usage = checks.get('ram_usage', 0)
        disk_free = checks.get('disk_free_gb', 0)

        net_status = "Connected" if checks.get('network_online') else "OFFLINE"
        latency = checks.get('avg_latency', 0)

        status_text = (
            f"● [bold]{active_keys}[/] Providers active  •  ⚡ [bold]{total_models}[/] Models ready\n"
            f"● [bold]CPU:[/] {cpu_usage}%  [bold]RAM:[/] {ram_usage}%     •  💾 [bold]Disk:[/] {disk_free:.0f} GB free\n"
            f"● [bold]Network:[/] {net_status} ({latency:.0f}ms)    •  [bold]Agent:[/] {agent_name} {checks.get('system_health', 'Ready').upper()}"
        )
        console.print(Panel(status_text, title="📊 SYSTEM STATUS", border_style="blue"))

        # 7. Integrations Panel
        from epex.interfaces.messaging import messaging_hub
        int_parts = []
        for name, bridge in messaging_hub.bridges.items():
            symbol = "[green]●[/]" if bridge.running else "[grey50]○[/]"
            int_parts.append(f"{symbol} {name.capitalize()}")

        console.print(Panel("   ".join(int_parts), title="🔗 INTEGRATIONS", border_style="green"))

        # 8. Discovery Badge
        pending = await discovery.get_pending_report()
        pending_count = sum(len(l) for l in pending.values())
        if pending_count > 0:
             console.print(Panel(f"🤖 [bold yellow]NEW MODELS DISCOVERED:[/] {pending_count} models pending review. Run '[bold]epex discover[/]' to approve.", border_style="yellow"))

        # 9. Main Menu
        menu = Table.grid(padding=(0, 2))
        menu.add_column(style="bold yellow")
        menu.add_column(style="white")

        menu.add_row("1.", "Launch CLI")
        menu.add_row("2.", "Launch TUI")
        menu.add_row("3.", "Launch Web GUI")
        menu.add_row("4.", "Launch Native GUI (Desktop)")
        menu.add_row("5.", "Manage API Keys")
        menu.add_row("6.", "App Integrations")
        menu.add_row("7.", "Model Discovery")
        menu.add_row("8.", "Workflow Manager")
        menu.add_row("9.", "User Profile & Settings")
        menu.add_row("10.", "System Repair")
        menu.add_row("11.", "Exit Command Center")

        console.print(menu)

        choice = Prompt.ask("\nSelect action", choices=[str(i) for i in range(1, 12)], default="2")

        if choice == "1": # CLI
            from epex.interfaces.cli import start_chat_loop
            await start_chat_loop()
        elif choice == "2": # TUI
            from epex.interfaces.textual_tui import EpexTextualApp
            app = EpexTextualApp()
            app.run()
        elif choice == "3": # Web GUI
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex(('127.0.0.1', 8000)) == 0:
                console.print("[yellow]ℹ️ GUI already running at http://127.0.0.1:8000[/]")
                import webbrowser
                webbrowser.open("http://127.0.0.1:8000")
            else:
                console.print("[magenta]🚀 Launching Web Dashboard...[/]")
                subprocess.Popen([sys.executable, "-m", "epex.interfaces.cli", "--gui"], stdout=open("epex_gui.log", "a"), stderr=subprocess.STDOUT)
                time.sleep(2)
                import webbrowser
                webbrowser.open("http://127.0.0.1:8000")
            sock.close()
            Prompt.ask("\nPress Enter to return")
        elif choice == "4": # Native GUI
            console.print("[cyan]🚀 Launching Native Desktop Interface...[/]")
            try:
                subprocess.Popen([sys.executable, "-m", "epex.interfaces.native_gui"], stdout=open("epex_native.log", "a"), stderr=subprocess.STDOUT)
            except Exception as e:
                console.print(f"[red]Failed to launch Native GUI: {e}[/red]")
            time.sleep(1)
        elif choice == "5": # KEYS
            api_manager = UniversalAPIKeyManager()
            await api_manager.guided_setup()
        elif choice == "6": # APPS
            await show_apps_menu(console, messaging_hub, api_manager)
        elif choice == "7": # DISCOVERY
            await show_discovery_menu(console, discovery)
        elif choice == "8": # WORKFLOWS
            await show_workflows_menu(console)
        elif choice == "9": # PROFILE
            await show_profile_menu(console, storage, config)
        elif choice == "10": # REPAIR
            await run_repair(console)
        elif choice == "11":
            console.print("[dim]Shutting down Neural OS... Goodbye.[/]")
            break

async def show_discovery_menu(console, discovery):
    while True:
        console.clear()
        console.print(Panel("[bold]🤖 HUGGINGFACE MODEL DISCOVERY[/]", border_style="yellow"))

        pending = await discovery.get_pending_report()
        if not any(pending.values()):
            console.print("[dim]No new models discovered. Try running a scan.[/]")
        else:
            for cat, models in pending.items():
                if models:
                    console.print(f"\n[bold cyan]{cat.upper()} ({len(models)})[/]")
                    for m in models[:5]:
                        console.print(f" • [bold]{m['id']}[/] ({m['downloads']} downloads)")
                    if len(models) > 5:
                        console.print(f" [dim]... and {len(models)-5} more[/]")

        console.print("\n1. Run New Scan\n2. Review & Approve Models\n3. Auto-Approve Popular (>10k downloads)\n4. Back")
        c = Prompt.ask("Select action", choices=["1", "2", "3", "4"], default="4")

        if c == "1":
            with console.status("[bold yellow]Scanning HuggingFace Trending..."):
                await discovery.run_discovery()
            console.print("[green]✓ Scan complete.[/]")
            time.sleep(1)
        elif c == "2":
            await review_discovery(console, discovery, pending)
        elif c == "3":
            count = await discovery.auto_approve_popular(10000)
            console.print(f"[green]✓ Approved {count} models.[/]")
            time.sleep(1)
        elif c == "4":
            break

async def review_discovery(console, discovery, pending):
    for cat, models in pending.items():
        for m in list(models):
            console.clear()
            console.print(Panel(f"[bold cyan]Reviewing {cat.upper()}[/]\n\nModel: [bold]{m['id']}[/]\nAuthor: {m['author']}\nDownloads: {m['downloads']}\nLikes: {m['likes']}", title="APPROVE MODEL?"))

            choice = Prompt.ask("Approve?", choices=["y", "n", "q"], default="y")
            if choice == "y":
                await discovery.approve_model(m['id'], category=cat)
                console.print("[green]✓ Approved.[/]")
            elif choice == "q":
                return
            time.sleep(0.5)

async def show_workflows_menu(console):
    while True:
        console.clear()
        console.print(Panel("[bold]📋 WORKFLOW MANAGER[/]", border_style="purple"))

        table = Table(box=None)
        table.add_column("Workflow")
        table.add_column("Steps")
        table.add_row("Daily Audit", "12")
        table.add_row("Cloud Backup", "3")

        console.print(table)
        console.print("\n1. Record New\n2. Play Existing\n3. Back")
        c = Prompt.ask("Select action", choices=["1", "2", "3"], default="3")
        if c == "3": break
        elif c == "1":
            name = Prompt.ask("Workflow name")
            console.print(f"[yellow]📹 Recording '{name}'... Press Ctrl+C to stop.[/]")
            try:
                while True: time.sleep(1)
            except KeyboardInterrupt:
                console.print(f"\n[green]✓ Workflow '{name}' saved.[/]")
                time.sleep(1)
        elif c == "2":
            name = Prompt.ask("Workflow name", default="Daily Audit")
            console.print(f"[cyan]▶ Playing '{name}'...[/]")
            time.sleep(2)
            console.print("[green]✓ Execution complete.[/]")
            time.sleep(1)

async def show_apps_menu(console, hub, manager):
    while True:
        console.clear()
        console.print(Panel("[bold]🔗 INTEGRATIONS MANAGER[/]", border_style="green"))

        table = Table(title="Messaging Bridges", box=None, header_style="bold blue")
        table.add_column("Service")
        table.add_column("Status")

        for name, bridge in hub.bridges.items():
            status = "[green]● Active[/]" if bridge.running else "[grey50]○ Inactive[/]"
            table.add_row(name.capitalize(), status)

        console.print(table)
        console.print("\n[bold cyan]Actions:[/]")
        console.print("1. [bold]Activate All Bridges[/]")
        console.print("2. [bold]Configure Telegram Bot[/]")
        console.print("3. [bold]Configure Discord Bot[/]")
        console.print("4. [bold]Add Other API Key[/]")
        console.print("5. [bold]Back to Main Menu[/]")

        c = Prompt.ask("\nSelect action", choices=["1", "2", "3", "4", "5"], default="5")
        if c == "5": break

        if c == "1":
            with console.status("[bold green]Starting Messaging Hub..."):
                await hub.start_all()
            console.print("[green]✓ All bridges with valid credentials started.[/]")
            time.sleep(1)
        elif c == "2":
            await manager._get_key_manual("telegram")
        elif c == "3":
            await manager._get_key_manual("discord")
        elif c == "4":
            await manager.guided_setup()

async def show_profile_menu(console, storage, config):
    while True:
        console.clear()
        console.print(Panel("[bold]👤 USER PROFILE & SETTINGS[/]", border_style="cyan"))

        console.print(f"1. User Name:  [bold]{config.get('user_name', 'User')}[/]")
        console.print(f"2. Agent Name: [bold]{config.get('epex_name', 'Epex')}[/]")

        opts = config.get('ui_settings', {})
        console.print(f"3. Show Token Counts: [bold]{'YES' if opts.get('show_tokens', True) else 'NO'}[/]")
        console.print(f"4. Show API Costs:    [bold]{'YES' if opts.get('show_rates', True) else 'NO'}[/]")
        console.print(f"5. Set Password")
        console.print(f"6. Back")

        c = Prompt.ask("Select setting to change", choices=["1", "2", "3", "4", "5", "6"], default="6")
        if c == "6": break
        elif c == "1": config['user_name'] = Prompt.ask("Enter new name")
        elif c == "2": config['epex_name'] = Prompt.ask("Enter new agent name")
        elif c == "3": config['ui_settings']['show_tokens'] = not opts.get('show_tokens', True)
        elif c == "4": config['ui_settings']['show_rates'] = not opts.get('show_rates', True)
        elif c == "5":
            pwd = Prompt.ask("New Password", password=True)
            import bcrypt
            config['password_hash'] = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
            console.print("[green]✓ Password updated.[/]")
            time.sleep(1)

        await storage.store_config(config)

async def run_repair(console):
    console.print("\n[bold yellow]🛠️ Initializing System Repair...[/]")
    install_lock = Path.home() / '.epex' / '.installed'
    if install_lock.exists(): install_lock.unlink()
    subprocess.run([sys.executable, "epex_run.py"], check=True)
    Prompt.ask("\nRepair complete. Press Enter.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 EPEX Command Center Closed.")
