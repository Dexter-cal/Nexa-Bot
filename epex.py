import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

async def check_environment():
    """Ensure all dependencies are met without redundant scanning"""
    install_lock = Path.home() / '.epex' / '.installed'
    if install_lock.exists():
        return

    try:
        import rich
        import psutil
        import cryptography
        import aiohttp
        # If imports work, create the lock
        install_lock.parent.mkdir(parents=True, exist_ok=True)
        install_lock.touch()
    except ImportError:
        print("📦 Missing core dependencies. Launching EPEX Repair & Install...")
        subprocess.run([sys.executable, "epex_run.py"], check=True)
        # Restart the script after repair
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
    from epex.core.constants import BANNER, VERSION
    from epex.foundation.storage import SecureConfigStorage

    console = Console()
    console.clear()

    # 1. Show Banner
    console.print(Align.center(f"[bold cyan]{BANNER}[/]"))
    console.print(Align.center(f"[italic sky_blue1]v{VERSION} | The Neural Operating System[/]\n"))

    # 2. Check Config & Setup
    if not await check_config():
        # If setup just finished, reload
        os.execv(sys.executable, ['python3'] + sys.argv)

    storage = SecureConfigStorage()
    config = await storage.load_config()

    # 3. Password Protection & Session Memory
    if config.get('password_hash'):
        import bcrypt
        import time
        last_login = config.get('last_login_time', 0)
        session_timeout = 3600 # 1 hour

        if time.time() - last_login > session_timeout:
            console.print("[bold yellow]🔐 This EPEX instance is password protected.[/]")
            attempts = 0
            while attempts < 3:
                pwd = Prompt.ask("Enter Password", password=True)
                if bcrypt.checkpw(pwd.encode(), config['password_hash'].encode()):
                    console.print("[green]✓ Access Granted.[/]\n")
                    config['last_login_time'] = time.time()
                    await storage.store_config(config)
                    break
                else:
                    attempts += 1
                    console.print(f"[red]✗ Incorrect password. ({3 - attempts} attempts left)[/]")
            else:
                console.print("[bold red]Access Denied. Locking system.[/]")
                return
        else:
            console.print("[dim green]✓ Session active. (Last login: {:.1f}m ago)[/]\n".format((time.time() - last_login)/60))

    # 4. Personalized Greeting
    user_name = config.get('user_name', 'User')
    preferred = config.get('preferred_interface', '1')
    # Map name to number if stored as string
    if preferred == "TUI": preferred = "1"
    elif preferred == "GUI": preferred = "2"
    elif preferred == "CLI": preferred = "3"

    console.print(Panel(f"Welcome back, [bold cyan]{user_name}[/]. How would you like to interact with EPEX today?"))

    # 5. Launch Menu
    console.print("\n[bold]Launch Options:[/]")
    console.print("1. [bold cyan]TUI[/] - Fast, adaptive terminal interface")
    console.print("2. [bold magenta]GUI[/] - High-fidelity web dashboard")
    console.print("3. [bold white]CLI[/] - Raw neural command line")
    console.print("4. [bold green]KEYS[/] - Connect and test AI providers")
    console.print("5. [bold yellow]REPAIR[/] - Fix dependencies and system health")
    console.print("6. [bold red]EXIT[/]")

    choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5", "6"], default=preferred)

    # Save preference
    if choice in ["1", "2", "3"]:
        iface_map = {"1": "TUI", "2": "GUI", "3": "CLI"}
        config['preferred_interface'] = iface_map[choice]
        await storage.store_config(config)

    if choice == "1":
        from epex.interfaces.tui import EpexTUI
        tui = EpexTUI()
        await tui.run()
    elif choice == "2":
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        if result == 0:
            console.print("[yellow]ℹ️ GUI is already running at http://127.0.0.1:8000[/]")
            import webbrowser
            webbrowser.open("http://127.0.0.1:8000")
        else:
            console.print("[magenta]🚀 Launching EPEX GUI Dashboard...[/]")
            # Launch GUI in background
            subprocess.Popen([sys.executable, "-m", "epex.interfaces.cli", "--gui"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            console.print("[dim]The dashboard should open in your browser at http://127.0.0.1:8000 shortly.[/]")
        sock.close()
    elif choice == "3":
        from epex.interfaces.cli import start_chat_loop
        await start_chat_loop()
    elif choice == "4":
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        manager = UniversalAPIKeyManager()
        await manager.guided_setup()
        os.execv(sys.executable, ['python3'] + sys.argv)
    elif choice == "5":
        console.print("[bold cyan]🔍 EPEX SYSTEM REPAIR & HEALTH CHECK[/]")
        console.print("1. [bold yellow]Re-run dependency check[/]")
        console.print("2. [bold green]Test all AI provider connections[/]")
        console.print("3. [bold red]Clear session and relog[/]")
        console.print("4. [bold white]Back[/]")

        repair_choice = Prompt.ask("\nSelect action", choices=["1", "2", "3", "4"], default="4")
        if repair_choice == "1":
            install_lock = Path.home() / '.epex' / '.installed'
            if install_lock.exists(): install_lock.unlink()
            subprocess.run([sys.executable, "epex_run.py"], check=True)
        elif repair_choice == "2":
            from epex.intelligence.api_manager import UniversalAPIKeyManager
            manager = UniversalAPIKeyManager()
            with console.status("[bold green]Testing all connections..."):
                status = await manager.get_connected_providers()
            for p, connected in status.items():
                symbol = "[green]✓[/]" if connected else "[red]✗[/]"
                console.print(f" {symbol} {p.capitalize()}")
            Prompt.ask("\nPress Enter to continue")
        elif repair_choice == "3":
            config['last_login_time'] = 0
            await storage.store_config(config)
            console.print("[green]✓ Session cleared.[/]")

        os.execv(sys.executable, ['python3'] + sys.argv)
    else:
        console.print("[dim]Goodbye.[/]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 EPEX Session Closed.")
