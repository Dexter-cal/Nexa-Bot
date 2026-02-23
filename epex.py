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

    # Only show this if we are actually checking
    print("🔍 Initializing EPEX Neural Environment...")
    try:
        import rich
        import psutil
        import cryptography
        import aiohttp
        import bcrypt
        import fastapi
        import uvicorn
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
    from rich.table import Table
    from epex.core.constants import BANNER, VERSION
    from epex.foundation.storage import SecureConfigStorage
    from epex.intelligence.api_manager import UniversalAPIKeyManager

    console = Console()
    storage = SecureConfigStorage()

    while True:
        console.clear()

        # 1. Show Banner
        console.print(Align.center(f"[bold cyan]{BANNER}[/]"))
        console.print(Align.center(f"[italic sky_blue1]v{VERSION} | The Neural Operating System[/]\n"))

        # 2. Check Config & Setup
        if not await check_config():
            # If setup just finished, reload
            os.execv(sys.executable, ['python3'] + sys.argv)

        config = await storage.load_config()

        # Initialize UI Settings if missing
        if 'ui_settings' not in config:
            config['ui_settings'] = {
                'show_model_count': True,
                'show_rates': True,
                'show_tokens': True
            }

        # 3. Password Protection & Session Memory
        if config.get('password_hash'):
            import bcrypt
            import time
            last_login = config.get('last_login_time', 0)
            session_timeout = 3600 # 1 hour

            if time.time() - last_login > session_timeout:
                console.print("[bold yellow]🔐 System Locked. Please authenticate.[/]")
                attempts = 0
                while attempts < 3:
                    pwd = Prompt.ask("Enter Password", password=True)
                    if bcrypt.checkpw(pwd.encode(), config['password_hash'].encode()):
                        console.print("[green]✓ Authentication Successful.[/]\n")
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
                pass # Session active
                # console.print("[dim green]✓ Session active. (Last login: {:.1f}m ago)[/]\n".format((time.time() - last_login)/60))

        # 4. Personalized Greeting & Status
        user_name = config.get('user_name', 'User')
        epex_name = config.get('epex_name', 'Epex')
        preferred = config.get('preferred_interface', '1')
        if preferred == "TUI": preferred = "1"
        elif preferred == "GUI": preferred = "2"
        elif preferred == "CLI": preferred = "3"

        # Status Summary Table
        status_table = Table.grid(expand=True)
        status_table.add_column(justify="left")
        status_table.add_column(justify="right")

        connected_keys = config.get('api_keys', {})
        online_count = len([k for k, v in connected_keys.items() if v])

        status_table.add_row(
            f"Welcome back, [bold cyan]{user_name}[/].",
            f"[dim]Agent: [bold]{epex_name}[/] | [green]●[/] {online_count} Keys Active[/]"
        )

        console.print(Panel(status_table, border_style="cyan"))

        # 5. Launcher Main Menu
        menu = Table.grid(padding=(0, 2))
        menu.add_column(style="bold cyan")
        menu.add_column(style="white")

        menu.add_row("1. TUI", "Launch Adaptive Terminal Interface")
        menu.add_row("2. GUI", "Open High-Fidelity Web Dashboard")
        menu.add_row("3. CLI", "Start Neural Command Line loop")
        menu.add_row("4. APPS", "Manage Connectivity (Telegram, Discord, etc.)")
        menu.add_row("5. MODELS", "Manage Intelligence Providers & Models")
        menu.add_row("6. REPAIR", "System Health, Dependencies & Repair")
        menu.add_row("7. EXIT", "Shutdown EPEX Neural OS")

        console.print(menu)

        choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5", "6", "7"], default=preferred)

        if choice == "1": # TUI
            from epex.interfaces.tui import EpexTUI
            tui = EpexTUI()
            await tui.run()

        elif choice == "2": # GUI
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 8000))
            if result == 0:
                console.print("[yellow]ℹ️ GUI is already running at http://127.0.0.1:8000[/]")
                try:
                    import webbrowser
                    webbrowser.open("http://127.0.0.1:8000")
                except:
                    console.print("[dim]Please open http://127.0.0.1:8000 in your browser.[/]")
            else:
                console.print("[magenta]🚀 Launching EPEX GUI Dashboard...[/]")
                log_file = open("epex_gui.log", "a")
                subprocess.Popen([sys.executable, "-m", "epex.interfaces.cli", "--gui"], stdout=log_file, stderr=log_file)
                console.print("[green]✓ GUI server started.[/]")
                import time
                time.sleep(2)
                try:
                    import webbrowser
                    webbrowser.open("http://127.0.0.1:8000")
                except: pass
            sock.close()
            Prompt.ask("\nPress Enter to return to launcher")

        elif choice == "3": # CLI
            from epex.interfaces.cli import start_chat_loop
            await start_chat_loop()

        elif choice == "4": # APPS SUBMENU
            while True:
                console.clear()
                console.print(Align.center(f"[bold cyan]{BANNER}[/]"))
                console.print(Panel("[bold]APP CONNECTIVITY MANAGER[/]", border_style="green"))

                # Check app status
                from epex.interfaces.messaging import messaging_hub
                app_table = Table(box=None, header_style="bold blue")
                app_table.add_column("Application")
                app_table.add_column("Status")
                app_table.add_column("Action")

                for app_id, bridge in messaging_hub.bridges.items():
                    status = "[green]✓ Active[/]" if bridge.running else "[grey50]○ Inactive[/]"
                    action = "Deactivate" if bridge.running else "Activate/Connect"
                    app_table.add_row(bridge.name, status, action)

                console.print(app_table)
                console.print("\n1. Connect Telegram\n2. Connect Discord\n3. Connect Slack\n4. Connect WhatsApp\n5. Back to Launcher")
                app_choice = Prompt.ask("Select action", choices=["1", "2", "3", "4", "5"], default="5")

                if app_choice == "5": break

                # Activate flow
                app_map = {"1": "telegram", "2": "discord", "3": "slack", "4": "whatsapp"}
                selected_app = app_map[app_choice]

                api_manager = UniversalAPIKeyManager()
                await api_manager.guided_setup() # In a real app we'd filter by app
                break

        elif choice == "5": # MODELS SUBMENU
            while True:
                console.clear()
                console.print(Align.center(f"[bold cyan]{BANNER}[/]"))

                # Model Settings
                ui_settings = config.get('ui_settings', {})

                # Display Current Stats
                manager = UniversalAPIKeyManager()
                connected_status = await manager.get_connected_providers()

                m_table = Table(title="INTELLIGENCE PROVIDERS", border_style="magenta")
                m_table.add_column("Provider")
                m_table.add_column("Status")
                if ui_settings.get('show_model_count'): m_table.add_column("Models")

                discovered = config.get('discovered_models', {})

                for p, online in connected_status.items():
                    status = "[green]ONLINE[/]" if online else "[red]OFFLINE[/]"
                    row = [p.capitalize(), status]
                    if ui_settings.get('show_model_count'):
                        count = len(discovered.get(p, []))
                        row.append(str(count) if online else "-")
                    m_table.add_row(*row)

                console.print(m_table)

                console.print("\n[bold]Model Display Settings:[/]")
                console.print(f"1. Toggle Model Count Display: [bold]{'ON' if ui_settings.get('show_model_count') else 'OFF'}[/]")
                console.print(f"2. Toggle Rates Display:      [bold]{'ON' if ui_settings.get('show_rates') else 'OFF'}[/]")
                console.print(f"3. Toggle Tokens Display:     [bold]{'ON' if ui_settings.get('show_tokens') else 'OFF'}[/]")
                console.print("4. Add/Connect New Provider Key")
                console.print("5. Search HuggingFace for Models")
                console.print("6. Back to Launcher")

                m_choice = Prompt.ask("\nSelect action", choices=["1", "2", "3", "4", "5", "6"], default="6")

                if m_choice == "6": break
                elif m_choice == "1": config['ui_settings']['show_model_count'] = not ui_settings.get('show_model_count')
                elif m_choice == "2": config['ui_settings']['show_rates'] = not ui_settings.get('show_rates')
                elif m_choice == "3": config['ui_settings']['show_tokens'] = not ui_settings.get('show_tokens')
                elif m_choice == "4":
                    await manager.guided_setup()
                elif m_choice == "5":
                    query = Prompt.ask("Search models (e.g. llama, vision)")
                    results = await manager.search_huggingface(query)
                    if results:
                        res_table = Table(title=f"Results for '{query}'")
                        res_table.add_column("Model ID")
                        for r in results[:10]: res_table.add_row(r['id'])
                        console.print(res_table)
                        Prompt.ask("Press Enter")

                await storage.store_config(config)

        elif choice == "6": # REPAIR
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

        elif choice == "7": # EXIT
            console.print("[dim]Goodbye.[/]")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 EPEX Session Closed.")
