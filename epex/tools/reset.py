import os
import shutil
import logging
from pathlib import Path
from epex.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class SystemResetTool(Tool):
    name = "system.full_reset"
    description = "Wipe all local configuration, soul files, and memory while preserving Quantum Snapshots (.qss). Reverts EPEX to a factory state."
    category = "system"
    risk_level = "critical"
    parameters = {
        "confirm": {"type": "boolean", "required": True, "description": "Must be True to proceed."}
    }

    async def execute(self, confirm: bool = False, **kwargs) -> ToolResult:
        if not confirm:
            return ToolResult(success=False, error="Reset aborted. Confirmation required.")

        epex_dir = Path.home() / ".epex"
        db_path = Path("epex.db")

        try:
            # 1. Preserve snapshots
            snapshot_dir = Path.home() / ".epex_backups"
            snapshot_dir.mkdir(exist_ok=True)

            for qss in Path(".").glob("*.qss"):
                shutil.move(str(qss), str(snapshot_dir / qss.name))

            # 2. Wipe directory
            if epex_dir.exists():
                shutil.rmtree(epex_dir)

            # 3. Wipe DB
            if db_path.exists():
                os.remove(db_path)

            logger.warning("🚨 SYSTEM RESET: All local state has been wiped.")

            return ToolResult(success=True, output="System reset complete. EPEX has been reverted to factory settings. Snapshots were moved to ~/.epex_backups/. Please restart the agent.")

        except Exception as e:
            logger.error(f"Reset failed: {e}")
            return ToolResult(success=False, error=str(e))
