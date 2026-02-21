import os
import sys
import asyncio
from pathlib import Path

async def main():
    print("⚡ EPEX APEX v5.0 - FAST LAUNCHER")
    print("---------------------------------")

    # 1. Environment Validation
    if sys.version_info < (3, 11):
        print("❌ EPEX requires Python 3.11 or higher.")
        return

    # 2. Check if configuration exists
    config_path = Path.home() / '.epex' / 'config.enc'

    if not config_path.exists():
        print("⚠️ No configuration found. Please run 'python epex_run.py' for full setup.")
        return

    # 3. Launch Preferred Interface
    try:
        from epex.foundation.storage import SecureConfigStorage
        storage = SecureConfigStorage()
        config = await storage.load_config()

        iface = config.get('preferred_interface', 'TUI')
        print(f"🚀 Launching {iface}...")

        if iface == 'GUI':
            from epex.interfaces.cli import launch_gui
            await launch_gui()
        elif iface == 'CLI':
            from epex.interfaces.cli import start_chat_loop
            await start_chat_loop()
        else: # TUI
            from epex.interfaces.tui import EpexTUI
            tui = EpexTUI()
            await tui.run()

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run 'python epex_run.py' to repair your installation.")
    except Exception as e:
        print(f"❌ Execution error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Epex Launcher closed.")
