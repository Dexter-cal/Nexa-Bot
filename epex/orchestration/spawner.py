import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from epex.orchestration.constants import MODES, ROLES
from epex.core.agent import Agent, AgentStatus

logger = logging.getLogger(__name__)

class AgentSpawner:
    """
    Spawn and manage specialized agents
    """
    def __init__(self, parent_id: str = "main"):
        self.parent_id = parent_id
        self.spawned_agents: Dict[str, Agent] = {}
        self.max_agents = 50
        from epex.core.resource_manager import AgentResourceManager
        self.resource_manager = AgentResourceManager(self)

    async def spawn_agent(self, role: str, task: Dict[str, Any], mode: str = 'assistive') -> Agent:
        # Aura-Driven Auto-Scaling
        from epex.core.engine import engine
        aura = engine.soul.data.get('current_aura', 'professional')

        # Adjust spawning priority or capacity based on aura
        if aura == "aggressive":
             # In aggressive mode, we might allow bypassing some soft limits or prioritize resources
             logger.info("Aggressive Aura detected: Prioritizing agent spawning.")

        if not await self.resource_manager.can_spawn():
            logger.warning("Resource limits reached. Cannot spawn more agents.")
            raise RuntimeError("Agent limit reached or insufficient resources")

        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        agent = Agent(agent_id, role, mode, self.parent_id)
        self.spawned_agents[agent_id] = agent

        logger.info(f"Spawned new agent: {agent_id} with role {role} in {mode} mode")

        # Start the agent
        await agent.start(task)

        return agent

    async def spawn_multiple(self, role_task_pairs: List[Any]) -> List[Agent]:
        agents = []
        for role, task in role_task_pairs:
            agent = await self.spawn_agent(role, task)
            agents.append(agent)
        return agents

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        agent = self.spawned_agents.get(agent_id)
        if not agent:
            return None
        return agent.to_dict()

    async def spawn_swarm(self, goal: str, count: int = 5) -> List[Agent]:
        """Spawn a swarm of specialized agents to achieve a complex goal in parallel"""
        from epex.intelligence.brain import StrategicPlanner
        planner = StrategicPlanner()

        logger.info(f"⚡ Swarm Orchestrator: Decomposing goal '{goal}' for parallel execution...")
        plan = await planner.create_plan(f"Break this goal into {count} parallel sub-goals: {goal}")

        sub_goals = plan.get('primary_strategy', [])
        if not sub_goals:
            # Fallback
            sub_goals = [{"description": f"Parallel segment {i} of {goal}"} for i in range(count)]

        agents = []
        for i, sub in enumerate(sub_goals[:count]):
            # Assign roles based on sub-goal description (simple keyword mapping)
            role = "assistant"
            desc = sub.get('description', '').lower()
            if "code" in desc: role = "developer"
            elif "security" in desc or "audit" in desc: role = "hacker"
            elif "research" in desc: role = "researcher"

            agent = await self.spawn_agent(role=role, task=sub, mode="autonomous")
            agents.append(agent)

        logger.info(f"✅ Swarm deployed: {len(agents)} agents coordinating on goal.")
        return agents

    async def terminate_agent(self, agent_id: str):
        if agent_id in self.spawned_agents:
            agent = self.spawned_agents[agent_id]
            await agent.terminate()
            del self.spawned_agents[agent_id]
            logger.info(f"Terminated agent: {agent_id}")
