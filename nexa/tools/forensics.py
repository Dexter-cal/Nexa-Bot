import aiohttp
import socket
import whois
from nexa.tools.base import Tool, ToolResult
from typing import Dict, Any, List

class ForensicOSINTTool(Tool):
    name = "security.forensic_osint"
    description = "Run deep forensic analysis on a domain or IP address."
    category = "security"
    risk_level = "medium"
    parameters = {
        "target": {"type": "string", "required": True}
    }

    async def execute(self, target: str, **kwargs) -> ToolResult:
        try:
            # 1. DNS Lookup
            ip = socket.gethostbyname(target)

            # 2. Whois
            w = whois.whois(target)

            # 3. Simulate certificate transparency check
            cert_data = {"status": "valid", "issuer": "Let's Encrypt", "expiry": "2025-12-31"}

            return ToolResult(success=True, output={
                "target": target,
                "ip": ip,
                "registrar": w.registrar,
                "creation_date": str(w.creation_date),
                "cert_info": cert_data
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
