import asyncio
import httpx
import logging
from typing import Dict, List, Any, Optional
from epex.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class EpexNetworkNode:
    """
    Handles peer-to-peer communication between multiple Epex instances.
    Supports task delegation, remote chat, and capability discovery.
    """
    def __init__(self):
        self.storage = SecureConfigStorage()
        self.peers: List[Dict[str, Any]] = []

    async def load_peers(self):
        config = await self.storage.load_config()
        self.peers = config.get('network_peers', [])

    async def add_peer(self, name: str, url: str, api_key: str):
        await self.load_peers()
        # Remove if exists
        self.peers = [p for p in self.peers if p['name'] != name]
        self.peers.append({
            "name": name,
            "url": url,
            "api_key": api_key,
            "status": "connected",
            "added_at": str(asyncio.get_event_loop().time())
        })
        config = await self.storage.load_config()
        config['network_peers'] = self.peers
        await self.storage.store_config(config)
        logger.info(f"Connected to peer: {name} at {url}")

    async def remove_peer(self, name: str):
        await self.load_peers()
        self.peers = [p for p in self.peers if p['name'] != name]
        config = await self.storage.load_config()
        config['network_peers'] = self.peers
        await self.storage.store_config(config)
        logger.info(f"Disconnected from peer: {name}")

    async def ping_peer(self, name: str) -> bool:
        try:
            res = await self.send_to_peer(name, "/api/v1/system/status", {}, method="GET")
            return res.get('status') == 'active'
        except Exception as e:
            logger.error(f"Failed to ping peer {name}: {e}")
            return False

    async def send_to_peer(self, peer_name: str, endpoint: str, data: Dict[str, Any] = None, method: str = "POST") -> Dict[str, Any]:
        peer = next((p for p in self.peers if p['name'] == peer_name), None)
        if not peer:
            raise ValueError(f"Peer '{peer_name}' not found.")

        url = f"{peer['url'].rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {"X-Epex-API-Key": peer['api_key']}

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "POST":
                response = await client.post(url, json=data, headers=headers)
            else:
                response = await client.get(url, headers=headers)
            return response.json()

    async def delegate_task(self, peer_name: str, command: str) -> Dict[str, Any]:
        return await self.send_to_peer(peer_name, "/api/v1/execute", {"command": command})

    async def broadcast(self, command: str) -> List[Dict[str, Any]]:
        results = []
        for peer in self.peers:
            try:
                res = await self.delegate_task(peer['name'], command)
                results.append({"peer": peer['name'], "result": res})
            except Exception as e:
                results.append({"peer": peer['name'], "error": str(e)})
        return results

    async def share_tool_with_peer(self, peer_name: str, tool_name: str) -> Dict[str, Any]:
        """Send a local tool's source code to a peer"""
        from epex.tools.registry import registry
        tool = registry.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found locally.")

        # In a real app, we'd need to find the source file or have the tool store its code
        # For now, we'll assume it's in a known directory or dynamically registered
        source_code = "# Tool source code placeholder"

        return await self.send_to_peer(peer_name, "/tools/receive", {
            "tool_name": tool_name,
            "source_code": source_code,
            "metadata": {"shared_from": "local-epex"}
        })

    async def request_tool_from_peer(self, peer_name: str, tool_name: str) -> Dict[str, Any]:
        """Request a specific tool from a peer"""
        return await self.send_to_peer(peer_name, "/tools/request", {"tool_name": tool_name})

network_node = EpexNetworkNode()
