import os
import subprocess
import sys

import asyncio
from pathlib import Path

async def main():
    print("🚀 EPEX APEX v5.0 - UNIFIED RUNNER")
    print("---------------------------------")

    # 1. Environment Validation
    if sys.version_info < (3, 11):
        print("❌ EPEX requires Python 3.11 or higher.")
        return

    # 2. Check if first run
    config_path = Path.home() / '.epex' / 'config.enc'

    if not config_path.exists():
        print("📝 No configuration found. Initializing Setup Wizard...")
        try:
            # Install dependencies if missing (simplified check)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"])

            from epex.interfaces.tui import TUISetupWizard
            wizard = TUISetupWizard()
            await wizard.run()
        except Exception as e:
            print(f"❌ Setup error: {e}")
    else:
        # Load config and launch preferred interface
        try:
            from epex.foundation.storage import SecureConfigStorage
            storage = SecureConfigStorage()
            config = await storage.load_config()

            iface = config.get('preferred_interface', 'TUI')
            print(f"✅ Configuration loaded. Launching {iface}...")

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

        except Exception as e:
            print(f"❌ Execution error: {e}")
            print("Hint: If your keys are corrupted, try deleting ~/.epex and rerunning.")

if __name__ == "__main__":
    asyncio.run(main())
