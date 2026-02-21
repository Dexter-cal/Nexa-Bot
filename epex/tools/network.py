from epex.tools.base import Tool, ToolResult
from typing import Optional, Dict, Any, List
import subprocess
import socket

class PingTool(Tool):
    name = "network.ping"
    description = "Ping a host to check connectivity"
    category = "network"
    risk_level = "low"
    parameters = {
        "host": {"type": "string", "required": True},
        "count": {"type": "integer", "required": False, "default": 4}
    }

    async def execute(self, host: str, count: int = 4, **kwargs) -> ToolResult:
        import asyncio
        import sys
        try:
            # Note: ping command might differ between OS
            if sys.platform == "win32":
                cmd = ["ping", "-n", str(count), host]
            else:
                cmd = ["ping", "-c", str(count), host]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                return ToolResult(success=True, output=stdout.decode())
            else:
                return ToolResult(success=False, error=stderr.decode() or "Ping failed")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class DNSLookupTool(Tool):
    name = "network.dns"
    description = "Perform a DNS lookup for a domain"
    category = "network"
    risk_level = "low"
    parameters = {
        "domain": {"type": "string", "required": True}
    }

    async def execute(self, domain: str, **kwargs) -> ToolResult:
        import asyncio
        try:
            # Use asyncio to avoid blocking
            ip_list = await asyncio.get_event_loop().getaddrinfo(domain, None)
            ips = list(set([res[4][0] for res in ip_list]))
            return ToolResult(success=True, output=ips)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class PortScanTool(Tool):
    name = "network.portscan"
    description = "Scan for open ports on a host"
    category = "network"
    risk_level = "medium"
    parameters = {
        "host": {"type": "string", "required": True},
        "ports": {"type": "list", "required": False, "default": [80, 443, 22]}
    }

    async def execute(self, host: str, ports: List[int] = [80, 443, 22], **kwargs) -> ToolResult:
        open_ports = []
        try:
            for port in ports:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    if s.connect_ex((host, port)) == 0:
                        open_ports.append(port)
            return ToolResult(success=True, output=open_ports)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
