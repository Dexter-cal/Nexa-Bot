import asyncio
from typing import List, Dict, Any
import logging
from nexa.core.agent import Agent

logger = logging.getLogger(__name__)

class SwarmCoordinator:
    """
    Coordinate a swarm of agents to achieve a common goal
    """
    def __init__(self, agents: List[Agent]):
        self.agents = agents

    async def execute(self) -> List[Dict[str, Any]]:
        logger.info(f"Coordinating swarm of {len(self.agents)} agents...")

        # In a real scenario, this would involve complex task distribution and result aggregation
        # For now, we wait for all agents to complete their assigned tasks
        results = await asyncio.gather(*[agent.wait() for agent in self.agents])

        # Flatten and return results
        flat_results = [item for sublist in results for item in sublist]
        logger.info("Swarm execution complete.")
        return flat_results

    async def broadcast(self, message: Dict[str, Any]):
        """Send a message to all agents in the swarm"""
        for agent in self.agents:
            await agent.send_message(message)
