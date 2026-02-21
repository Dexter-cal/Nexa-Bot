import psutil
from typing import Dict, Any

class AgentResourceManager:
    """
    Manage resources across spawned agents
    """

    def __init__(self, spawner):
        self.spawner = spawner

        # Limits per agent
        self.per_agent_limits = {
            'cpu_percent': 10.0,
            'memory_mb': 500.0,
        }

        # Global limits
        self.global_limits = {
            'total_cpu_percent': 80.0,
            'total_memory_mb': 8000.0,
        }

    async def can_spawn(self) -> bool:
        """
        Check if we can spawn another agent based on current resource usage
        """
        # Check count limit
        if len(self.spawner.spawned_agents) >= self.spawner.max_agents:
            return False

        # Check resource usage
        usage = self.get_total_usage()

        if usage['cpu'] > self.global_limits['total_cpu_percent']:
            return False

        if usage['memory'] > self.global_limits['total_memory_mb']:
            return False

        return True

    def get_total_usage(self) -> Dict[str, float]:
        """
        Get total resource usage across all agents
        """
        total_cpu = sum(
            a.cpu_usage
            for a in self.spawner.spawned_agents.values()
        )

        total_memory = sum(
            a.memory_usage
            for a in self.spawner.spawned_agents.values()
        )

        return {
            'cpu': total_cpu,
            'memory': total_memory
        }
