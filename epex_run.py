import os
import subprocess
import sys

import asyncio
from pathlib import Path

async def main():
    print("🛠️ EPEX APEX v5.0 - INSTALLER & REPAIR")
    print("--------------------------------------")

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--safe-mode", action="store_true", help="Bypass plugin loading and use minimal core.")
    args = parser.parse_args()

    if args.safe_mode:
        print("🛡️ SAFE MODE ACTIVATED: Skipping extended modules...")
        os.environ["EPEX_SAFE_MODE"] = "true"

    # 1. Environment Validation
    if sys.version_info < (3, 11):
        print("❌ EPEX requires Python 3.11 or higher.")
        return

    # 2. Check if first run
    config_path = Path.home() / '.epex' / 'config.enc'

    # 2. Dependency Check (Smart)
    print("🔍 Checking system dependencies...")
    try:
        import importlib.metadata
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", "r") as f:
                required = [line.split("==")[0].split(">=")[0].strip() for line in f if line.strip() and not line.startswith("#")]

            installed = {dist.metadata['Name'].lower() for dist in importlib.metadata.distributions()}
            missing = [r for r in required if r.lower() not in installed and r.lower().replace("-", "_") not in installed]

            if missing:
                print(f"📦 Installing missing packages: {', '.join(missing)}")
                subprocess.run([sys.executable, "-m", "pip", "install", *missing, "--quiet"], check=True)
            else:
                print("✅ All dependencies satisfied.")

        # Ensure EPEX is installed in editable mode
        print("🔗 Linking EPEX modules...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"], check=True)
    except Exception as e:
        print(f"⚠️ Dependency check warning: {e}")

    # 3. Check for Virtual Environment
    if not (sys.prefix != sys.base_prefix or 'VIRTUAL_ENV' in os.environ):
        print("⚠️  Warning: You are not running in a virtual environment.")
        print("💡 Recommended: Create a venv with 'python -m venv venv' and activate it.")

    if not config_path.exists():
        print("📝 No configuration found. Initializing Setup Wizard...")
        try:
            from epex.interfaces.tui import TUISetupWizard
            wizard = TUISetupWizard()
            await wizard.run()

            # Offer Global Shortcut
            home = Path.home()
            bashrc = home / ".bashrc"
            zshrc = home / ".zshrc"
            shell_configs = [bashrc, zshrc]

            launcher_path = Path(__file__).parent / "epex.py"
            alias_line = f"alias epex='python3 {launcher_path.absolute()}'"

            print("\n💡 Tip: Would you like to add 'epex' as a global command?")
            choice = input("Add alias to your shell profile? (y/n): ")
            if choice.lower() == 'y':
                added = False
                for config in shell_configs:
                    if config.exists():
                        with open(config, "r") as f:
                            content = f.read()
                        if alias_line not in content:
                            with open(config, "a") as f:
                                f.write(f"\n# EPEX APEX Shortcut\n{alias_line}\n")
                            print(f"✅ Alias added to {config.name}")
                            added = True
                        else:
                            print(f"ℹ️  Alias already exists in {config.name}")
                            added = True

                if added:
                    print("🚀 Please restart your terminal or run 'source <your_shell_config>'")
                else:
                    print("⚠️  No shell profile (.bashrc or .zshrc) found. Manual alias creation required.")

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

            # Run the unified launcher
            launcher_path = Path(__file__).parent / "epex.py"
            subprocess.run([sys.executable, str(launcher_path)])

        except Exception as e:
            print(f"❌ Execution error: {e}")
            print("Hint: If your keys are corrupted, try deleting ~/.epex and rerunning.")

if __name__ == "__main__":
    asyncio.run(main())
