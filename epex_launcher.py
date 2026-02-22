import os
import sys
import asyncio
import subprocess
from pathlib import Path

async def main():
    # Redirect to the unified launcher
    launcher_path = Path(__file__).parent / "epex.py"
    if launcher_path.exists():
        subprocess.run([sys.executable, str(launcher_path)])
    else:
        print("❌ Error: epex.py launcher not found.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Epex Launcher closed.")
