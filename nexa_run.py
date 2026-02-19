import os
import subprocess
import sys

def setup():
    print("🚀 NEXA BOT - AUTO-INSTALLER")
    print("----------------------------")

    # 1. Check Python version
    if sys.version_info < (3, 11):
        print("❌ Nexa requires Python 3.11 or higher.")
        return

    # 2. Install dependencies
    print("📦 Installing core dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return

    # 3. Launch Express Setup
    print("✅ Core systems ready.")
    print("Launching Nexa Express Setup...")

    try:
        from nexa.interfaces.cli import run_quick_setup
        import asyncio
        asyncio.run(run_quick_setup())
    except ImportError:
        print("❌ Could not launch setup. Make sure you are in the nexa root directory.")
    except Exception as e:
        print(f"❌ Error during setup: {e}")

if __name__ == "__main__":
    setup()
