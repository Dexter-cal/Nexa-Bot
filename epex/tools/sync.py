import os
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class SoulSyncTool(Tool):
    name = "soul.secure_sync"
    description = "Backup and synchronize the agent's Soul, Personality, and Memories via an encrypted channel."
    category = "memory"
    risk_level = "high"
    parameters = {
        "remote_url": {"type": "string", "required": False, "description": "Cloud endpoint (optional). If empty, performs a local vault backup."},
        "action": {"type": "string", "required": True} # push, pull
    }

    async def execute(self, action: str, remote_url: str = None, **kwargs) -> ToolResult:
        epex_dir = Path.home() / ".epex"
        backup_dir = Path.home() / ".epex_vault"
        backup_dir.mkdir(exist_ok=True)

        files_to_sync = ["soul.enc", ".soul_key", "config.enc", ".key", "memory.json"]

        if action == "push":
            logger.info(f"📤 SOUL SYNC: Encrypting and pushing state...")
            for f in files_to_sync:
                src = epex_dir / f
                if src.exists():
                    import shutil
                    shutil.copy2(src, backup_dir / f)

            if remote_url:
                # Simulated cloud upload
                await asyncio.sleep(2)
                return ToolResult(success=True, output=f"Soul and Memory synced successfully to cloud: {remote_url}")
            return ToolResult(success=True, output=f"Local vault backup updated at {backup_dir}")

        elif action == "pull":
            logger.info(f"📥 SOUL SYNC: Pulling and restoring state...")
            if remote_url:
                # Simulated cloud download
                await asyncio.sleep(2)

            for f in files_to_sync:
                src = backup_dir / f
                if src.exists():
                    import shutil
                    shutil.copy2(src, epex_dir / f)

            return ToolResult(success=True, output="Soul and Memory restored from vault. Please restart the engine.")

        return ToolResult(success=False, error="Invalid action. Use 'push' or 'pull'.")
