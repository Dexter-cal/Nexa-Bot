import os
import tarfile
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from epex.tools.base import Tool, ToolResult
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class QuantumSnapshotTool(Tool):
    name = "meta.quantum_snapshot"
    description = "Export the entire agent state (Soul, Memory, Config, DB) as a single portable encrypted snapshot."
    category = "meta"
    risk_level = "high"
    parameters = {
        "output_path": {"type": "string", "required": False, "description": "Destination path for the snapshot. Defaults to 'epex_snapshot.qss'"},
        "include_db": {"type": "boolean", "required": False, "default": True}
    }

    async def execute(self, output_path: str = "epex_snapshot.qss", include_db: bool = True, **kwargs) -> ToolResult:
        epex_dir = Path.home() / ".epex"
        files_to_pack = [
            epex_dir / "config.enc",
            epex_dir / ".key",
            epex_dir / "soul.enc",
            epex_dir / ".soul_key"
        ]

        if include_db:
            if os.path.exists("epex.db"):
                files_to_pack.append(Path("epex.db"))
            elif os.path.exists("nexa.db"):
                files_to_pack.append(Path("nexa.db"))

        # Filter existing files
        files_to_pack = [f for f in files_to_pack if f.exists()]

        if not files_to_pack:
            return ToolResult(success=False, error="No state files found to snapshot.")

        temp_tar = "temp_snapshot.tar.gz"
        try:
            with tarfile.open(temp_tar, "w:gz") as tar:
                for f in files_to_pack:
                    tar.add(f, arcname=f.name)

            # Encrypt the tarball
            # Use the master key from .epex/.key if available, otherwise generate a temporary one
            key_path = epex_dir / ".key"
            if key_path.exists():
                key = key_path.read_bytes()
            else:
                key = Fernet.generate_key() # Should not happen if files exist

            cipher = Fernet(key)
            with open(temp_tar, "rb") as f:
                data = f.read()

            encrypted_data = cipher.encrypt(data)

            with open(output_path, "wb") as f:
                f.write(encrypted_data)

            return ToolResult(success=True, output={
                "message": f"Quantum Snapshot created at {output_path}",
                "files_included": [f.name for f in files_to_pack],
                "size_bytes": len(encrypted_data)
            })

        except Exception as e:
            logger.exception(f"Snapshot failed: {e}")
            return ToolResult(success=False, error=str(e))
        finally:
            if os.path.exists(temp_tar):
                os.remove(temp_tar)

class QuantumRestoreTool(Tool):
    name = "meta.quantum_restore"
    description = "Restore the agent state from a Quantum Snapshot."
    category = "meta"
    risk_level = "critical"
    parameters = {
        "snapshot_path": {"type": "string", "required": True, "description": "Path to the .qss snapshot file"}
    }

    async def execute(self, snapshot_path: str, **kwargs) -> ToolResult:
        if not os.path.exists(snapshot_path):
            return ToolResult(success=False, error=f"Snapshot file not found: {snapshot_path}")

        epex_dir = Path.home() / ".epex"
        key_path = epex_dir / ".key"

        if not key_path.exists():
            return ToolResult(success=False, error="Master key not found. Restore impossible without the original key.")

        try:
            key = key_path.read_bytes()
            cipher = Fernet(key)

            with open(snapshot_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = cipher.decrypt(encrypted_data)

            temp_tar = "temp_restore.tar.gz"
            with open(temp_tar, "wb") as f:
                f.write(decrypted_data)

            with tarfile.open(temp_tar, "r:gz") as tar:
                # We need to be careful where we extract.
                # For DB, it might be in the current directory.
                # For others, in ~/.epex/
                for member in tar.getmembers():
                    if member.name.endswith(".db"):
                        tar.extract(member, path=".")
                    else:
                        tar.extract(member, path=epex_dir)

            return ToolResult(success=True, output="Quantum Restore complete. Please restart the engine to apply changes.")

        except Exception as e:
            logger.exception(f"Restore failed: {e}")
            return ToolResult(success=False, error=str(e))
        finally:
            if os.path.exists(temp_tar):
                os.remove(temp_tar)
