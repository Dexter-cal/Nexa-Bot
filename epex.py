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

    while True:
        console.clear()

        # 1. Show Banner (Updated design)
        console.print(Align.center(f"[bold cyan]{BANNER}[/]"))
        console.print(Align.center(f"[italic sky_blue1]v{VERSION} | Your AI Command Center[/]\n"))

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
        user_name = config.get('user_name', 'User')
        agent_name = config.get('epex_name', 'Epex')

        console.print(Panel(
            f"👤 Welcome back, [bold cyan]{user_name}[/]!\nAgent: [bold]{agent_name}[/]  •  Last active: [dim]{last_active}[/]",
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
            Panel("[bold magenta]🎨 GUI[/]\n[dim]Desktop\nApp[/]", border_style="magenta", width=25)
        )
        console.print(iface_table)

        # 6. System Status Panel
        api_manager = UniversalAPIKeyManager()
        keys = config.get('api_keys', {})
        active_keys = len([k for k, v in keys.items() if v])

        # Discovered models count
        discovered = config.get('discovered_models', {})
        total_models = sum(len(m_list) for m_list in discovered.values())

        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_free = psutil.disk_usage('/').free / (1024**3)

        status_text = (
            f"● [bold]{active_keys}[/] API keys connected  •  ⚡ [bold]{total_models}[/] models discovered\n"
            f"● [bold]CPU:[/] {cpu_usage}%  [bold]RAM:[/] {ram_usage}%     •  💾 [bold]Disk:[/] {disk_free:.0f} GB free\n"
            f"● [bold]Network:[/] Connected        •  [bold]Agent:[/] {agent_name} Ready"
        )
        console.print(Panel(status_text, title="📊 SYSTEM STATUS", border_style="blue"))

        # 7. Integrations Panel
        from epex.interfaces.messaging import messaging_hub
        int_parts = []
        for name, bridge in messaging_hub.bridges.items():
            symbol = "[green]●[/]" if bridge.running else "[grey50]○[/]"
            int_parts.append(f"{symbol} {name.capitalize()}")

        console.print(Panel("   ".join(int_parts), title="🔗 INTEGRATIONS", border_style="green"))

        # 8. Main Menu
        menu = Table.grid(padding=(0, 2))
        menu.add_column(style="bold yellow")
        menu.add_column(style="white")

        menu.add_row("1.", "Launch CLI")
        menu.add_row("2.", "Launch TUI")
        menu.add_row("3.", "Launch GUI")
        menu.add_row("4.", "Manage API Keys")
        menu.add_row("5.", "App Integrations")
        menu.add_row("6.", "User Profile & Settings")
        menu.add_row("7.", "System Repair")
        menu.add_row("8.", "Exit Command Center")

        console.print(menu)

        choice = Prompt.ask("\nSelect action", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="2")

        if choice == "1": # CLI
            from epex.interfaces.cli import start_chat_loop
            await start_chat_loop()
        elif choice == "2": # TUI
            from epex.interfaces.tui import EpexTUI
            tui = EpexTUI()
            await tui.run()
        elif choice == "3": # GUI
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex(('127.0.0.1', 8000)) == 0:
                console.print("[yellow]ℹ️ GUI already running at http://127.0.0.1:8000[/]")
                import webbrowser
                webbrowser.open("http://127.0.0.1:8000")
            else:
                console.print("[magenta]🚀 Launching GUI Dashboard...[/]")
                subprocess.Popen([sys.executable, "-m", "epex.interfaces.cli", "--gui"], stdout=open("epex_gui.log", "a"), stderr=subprocess.STDOUT)
                time.sleep(2)
                import webbrowser
                webbrowser.open("http://127.0.0.1:8000")
            sock.close()
            Prompt.ask("\nPress Enter to return")
        elif choice == "4": # KEYS
            await api_manager.guided_setup()
        elif choice == "5": # APPS
            await show_apps_menu(console, messaging_hub, api_manager)
        elif choice == "6": # PROFILE
            await show_profile_menu(console, storage, config)
        elif choice == "7": # REPAIR
            await run_repair(console)
        elif choice == "8":
            console.print("[dim]Shutting down Neural OS... Goodbye.[/]")
            break

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
