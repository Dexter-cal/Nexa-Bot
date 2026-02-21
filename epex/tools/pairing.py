import os
import logging
import json
import base64
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult
from rich.console import Console
from rich.panel import Panel
import io

logger = logging.getLogger(__name__)

class GeneratePairingQRTool(Tool):
    name = "system.generate_pairing_qr"
    description = "Generate a secure QR code and config string to instantly link a mobile app or another PC."
    category = "system"
    risk_level = "medium"
    parameters = {}

    async def execute(self, **kwargs) -> ToolResult:
        from epex.foundation.storage import SecureConfigStorage
        storage = SecureConfigStorage()
        config = await storage.load_config()

        # Data to encode
        pairing_data = {
            "name": config.get("epex_name", "Epex-Bot"),
            "url": "http://localhost:8000", # Should be public IP/Tunnel URL in prod
            "key": "nxa_" + base64.b64encode(os.urandom(16)).decode(),
            "version": "3.5"
        }

        config_str = base64.b64encode(json.dumps(pairing_data).encode()).decode()

        # ASCII QR Code (Simplified)
        console = Console(file=io.StringIO(), force_terminal=True, width=40)
        qr_ascii = """
▄▄▄▄▄▄▄  ▄  ▄▄ ▄▄▄▄▄▄▄
█ ▄▄▄ █ ▀▄█▄▀█ █ ▄▄▄ █
█ ███ █ █▀▀▀▀█ █ ███ █
█▄▄▄▄▄█ █ █ █ █▄▄▄▄▄█
▄▄▄ ▄▄▄▄▄▀▀▄█▄▄ ▄ ▄ ▄
▀ ▀▄▄▀▀▄▄█▀▀▀▄▀▀█▄▀▀▀█
▄▀▄▄▄ ▄▀▄█▄ ▀▀▀█▄█▀▄▀
▄▄▄▄▄▄▄ █▄▀▀ ▀██ ▄ ███
█ ▄▄▄ █ ▄▀█▀ █▄▄▄█ █▄█
█ ███ █ █ █▀▀ ▀▄▄▀ ▀▀
█▄▄▄▄▄█ █▀█ ▀▀▀▀▄▀▄▀▄▀
"""
        console.print(Panel(qr_ascii, title="Scan with Epex Mobile", border_style="green"))
        console.print(f"Config String: [bold cyan]{config_str}[/]")

        return ToolResult(success=True, output=console.file.getvalue())
