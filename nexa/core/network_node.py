import asyncio
import httpx
import logging
from typing import Dict, List, Any, Optional
from nexa.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class NexaNetworkNode:
    """
    Handles peer-to-peer communication between multiple Nexa instances.
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
        self.peers.append({
            "name": name,
            "url": url,
            "api_key": api_key,
            "status": "connected"
        })
        config = await self.storage.load_config()
        config['network_peers'] = self.peers
        await self.storage.store_config(config)
        logger.info(f"Connected to peer: {name} at {url}")

    async def send_to_peer(self, peer_name: str, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        peer = next((p for p in self.peers if p['name'] == peer_name), None)
        if not peer:
            raise ValueError(f"Peer '{peer_name}' not found.")

        url = f"{peer['url'].rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {"X-Nexa-API-Key": peer['api_key']}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data, headers=headers)
            return response.json()

    async def delegate_task(self, peer_name: str, command: str) -> Dict[str, Any]:
        return await self.send_to_peer(peer_name, "/execute", {"command": command})

    async def broadcast(self, command: str) -> List[Dict[str, Any]]:
        results = []
        for peer in self.peers:
            try:
                res = await self.delegate_task(peer['name'], command)
                results.append({"peer": peer['name'], "result": res})
            except Exception as e:
                results.append({"peer": peer['name'], "error": str(e)})
        return results

network_node = NexaNetworkNode()
