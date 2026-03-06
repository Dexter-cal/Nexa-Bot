"""
Peer-to-Peer Networking Manager for EPEX APEX v5.0
Handles multi-instance connections, task delegation, and distributed intelligence.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from epex.core.network_node import network_node
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)

class NetworkingManager:
    """High-level manager for EPEX peer networking"""

    def __init__(self):
        self.console = Console()

    async def connect_to_peer(self, name: str, url: str, api_key: str = None):
        """Securely connect to a remote EPEX instance"""
        self.console.print(f"\n[cyan]⏳ Testing connection to peer '{name}'...[/cyan]")

        # Add temporarily to test
        await network_node.add_peer(name, url, api_key)

        result = await network_node.ping_peer(name)

        if result['online']:
            info = result['info']
            self.console.print(f"[green]✓ Connected to: {info.get('config', {}).get('epex_name', 'Remote EPEX')}[/green]")
            self.console.print(f"  Version: {info.get('config', {}).get('version', 'unknown')}")
            self.console.print(f"  Agents: {info.get('agents', 0)} active")
            self.console.print(f"  Latency: {result['latency']:.1f}ms")
            return True
        else:
            self.console.print(f"[red]✗ Failed to connect to peer: {result.get('error')}[/red]")
            await network_node.remove_peer(name)
            return False

    async def list_peers(self):
        """Display all connected peers and their real-time status"""
        await network_node.load_peers()

        if not network_node.peers:
            self.console.print("[dim]No peers connected yet.[/dim]")
            return

        table = Table(title="🌐 EPEX PEER NETWORK", border_style="cyan")
        table.add_column("Peer Name", style="bold cyan")
        table.add_column("URL", style="dim")
        table.add_column("Status", style="lime")
        table.add_column("Latency", justify="right")
        table.add_column("Agents", justify="right")

        # Ping all in parallel for fresh status
        pings = await asyncio.gather(*[network_node.ping_peer(p['name']) for p in network_node.peers])

        for i, p in enumerate(network_node.peers):
            ping = pings[i]
            status = "[green]● Online[/]" if ping['online'] else "[red]○ Offline[/]"
            latency = f"{ping['latency']:.0f}ms" if ping['online'] else "-"
            agents = str(ping.get('info', {}).get('agents', '-')) if ping['online'] else "-"

            table.add_row(p['name'], p['url'], status, latency, agents)

        self.console.print(table)

    async def delegate(self, peer_name: str, command: str):
        """Delegate a natural language command to a specific peer"""
        self.console.print(f"[dim]Delegating task to '{peer_name}'...[/dim]")
        try:
            result = await network_node.delegate_task(peer_name, command)
            return result
        except Exception as e:
            self.console.print(f"[red]Delegation failed: {e}[/red]")
            return None
