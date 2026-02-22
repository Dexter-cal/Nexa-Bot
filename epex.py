import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

async def check_environment():
    """Ensure all dependencies are met"""
    try:
        import rich
        import psutil
        import cryptography
        import aiohttp
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
    console.print(Align.center(f"[dim]Version {VERSION} | The Neural OS[/]\n"))

    # 2. Check Config & Setup
    if not await check_config():
        # If setup just finished, reload
        os.execv(sys.executable, ['python3'] + sys.argv)

    storage = SecureConfigStorage()
    config = await storage.load_config()

    # 3. Password Protection
    if config.get('password_hash'):
        import bcrypt
        console.print("[bold yellow]🔐 This EPEX instance is password protected.[/]")
        attempts = 0
        while attempts < 3:
            pwd = Prompt.ask("Enter Password", password=True)
            if bcrypt.checkpw(pwd.encode(), config['password_hash'].encode()):
                console.print("[green]✓ Access Granted.[/]\n")
                break
            else:
                attempts += 1
                console.print(f"[red]✗ Incorrect password. ({3 - attempts} attempts left)[/]")
        else:
            console.print("[bold red]Access Denied. Locking system.[/]")
            return

    # 4. Personalized Greeting
    user_name = config.get('user_name', 'User')
    console.print(Panel(f"Welcome back, [bold cyan]{user_name}[/]. How would you like to interact with EPEX today?"))

    # 5. Launch Menu
    console.print("\n[bold]Launch Options:[/]")
    console.print("1. [bold cyan]TUI[/] - Fast, adaptive terminal interface")
    console.print("2. [bold magenta]GUI[/] - High-fidelity web dashboard")
    console.print("3. [bold white]CLI[/] - Raw neural command line")
    console.print("4. [bold yellow]REPAIR[/] - Fix dependencies and check connectivity")
    console.print("5. [bold red]EXIT[/]")

    choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5"], default="1")

    if choice == "1":
        from epex.interfaces.tui import EpexTUI
        tui = EpexTUI()
        await tui.run()
    elif choice == "2":
        console.print("[magenta]🚀 Launching EPEX GUI Dashboard...[/]")
        # Launch GUI in background or as a command
        subprocess.Popen([sys.executable, "-m", "epex.interfaces.cli", "--gui"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        console.print("[dim]The dashboard should open in your browser shortly.[/]")
    elif choice == "3":
        from epex.interfaces.cli import start_chat_loop
        await start_chat_loop()
    elif choice == "4":
        subprocess.run([sys.executable, "epex_run.py"], check=True)
        os.execv(sys.executable, ['python3'] + sys.argv)
    else:
        console.print("[dim]Goodbye.[/]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 EPEX Session Closed.")
