import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from nexa.intelligence.router import EnhancedLLMRouter
from nexa.tools.registry import registry
from nexa.core.security import SecurityGuardian, GuardrailEngine
from nexa.models.core import Task
from nexa.core.database import AsyncSessionLocal
from nexa.orchestration.spawner import AgentSpawner
from nexa.intelligence.brain import StrategicPlanner
from nexa.intelligence.council import AICouncil

logger = logging.getLogger(__name__)

class TaskManager:
    """
    Manage tasks and their execution with planning and security
    """
    def __init__(self, llm_router=None, security_guardian=None):
        self.llm_router = llm_router or EnhancedLLMRouter()
        self.security_guardian = security_guardian or SecurityGuardian({})
        self.guardrail_engine = GuardrailEngine()
        self.spawner = AgentSpawner()
        self.planner = StrategicPlanner()
        self.council = AICouncil()
        self.queue = asyncio.Queue()
        self.active_tasks: List[Task] = []

    async def create_task_from_command(self, command: str) -> Task:
        async with AsyncSessionLocal() as session:
            # We need a user_id. For now we use a dummy one or fetch/create a default user
            from nexa.models.core import User
            from sqlalchemy import select
            result = await session.execute(select(User).limit(1))
            user = result.scalars().first()
            if not user:
                user = User(username="default", email="default@nexa.bot", password_hash="none")
                session.add(user)
                await session.commit()
                await session.refresh(user)

            task = Task(description=command, name=command[:50], user_id=user.id)
            session.add(task)
            await session.commit()
            await session.refresh(task)

        await self.queue.put(task)
        return task

    async def process_queue(self):
        if self.queue.empty():
            return

        task = await self.queue.get()
        async with AsyncSessionLocal() as session:
            task = await session.merge(task)
            task.status = "running"
            await session.commit()
            persistent_task = task
            self.active_tasks.append(persistent_task)

        try:
            result = await self.execute_task(persistent_task)
            async with AsyncSessionLocal() as session:
                task = await session.merge(persistent_task)
                task.result = result
                task.status = "completed"
                await session.commit()
        except Exception as e:
            logger.exception(f"Task failed: {e}")
            async with AsyncSessionLocal() as session:
                task = await session.merge(persistent_task)
                task.status = "failed"
                task.result = {"success": False, "error": str(e)}
                await session.commit()
        finally:
            if persistent_task in self.active_tasks:
                self.active_tasks.remove(persistent_task)

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Plan and execute a task
        """
        # 0. Handle simple direct questions/commands
        lower_desc = task.description.lower()
        if any(q in lower_desc for q in ["who created you", "who is your creator", "who made you"]):
             return await self.llm_router.execute(task.description)

        # Support for parallel agent spawning
        if "spawn" in lower_desc and "agent" in lower_desc:
             return await self._handle_spawn_command(task)

        # 1. Plan the task using Strategic Planner
        plan = await self.planner.create_plan(task.description)
        task.steps = plan.get('primary_strategy', [])

        if not task.steps and not plan.get('success', True):
            # Fallback to simple planning if strategic planner fails
            simple_plan = await self._plan_task_simple(task)
            task.steps = simple_plan.get('steps', [])

        # 2. Execute steps
        results = []
        for step in task.steps:
            # For critical steps, consult the council
            if task.priority == 'critical' or step.get('risk_level') == 'high':
                approved = await self.council.vote_on_action(step.get('description', 'Unknown action'))
                if not approved:
                    return {"success": False, "error": "Action rejected by AI Council", "step": step}

            result = await self._execute_step(step, task)
            results.append(result)
            if not result.success:
                # Try alternative strategy if available
                if plan.get('alternative_strategy'):
                    logger.warning("Primary strategy failed. Attempting alternative strategy...")
                    # Simplified: just log for now
                return {"success": False, "error": result.error, "step_results": results}

        # 3. Aggregate final result
        final_response = await self.llm_router.execute(
            f"Task: {task.description}\nSteps executed: {json.dumps(results, default=str)}\nSummarize final result."
        )

        return {"success": True, "response": final_response['response'], "steps": results}

    async def _plan_task_simple(self, task: Task) -> Dict[str, Any]:
        """Simple planning fallback"""
        available_tools = [t.name for t in registry.list_all()]
        prompt = f"Break this task into steps using these tools: {available_tools}. Task: {task.description}. Return JSON with 'steps' list."

        plan_response = await self.llm_router.execute(prompt)
        try:
            content = plan_response['response']
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            return json.loads(content)
        except:
            return {"steps": []}

    async def _execute_step(self, step: Dict[str, Any], task: Task):
        tool_name = step.get('tool')
        params = step.get('params', {})

        if not tool_name:
            # Fallback to LLM execution if no tool specified
            return await self.llm_router.execute(task.description)

        tool = registry.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        # Security check
        risk = self.security_guardian.assess_risk(tool_name, params)
        if self.security_guardian.require_approval(tool_name, risk):
            # In a real scenario, this would wait for user input
            logger.info(f"APPROVAL REQUIRED for {tool_name} with risk {risk}")
            # Mocking approval for now

        guardrail_check = await self.guardrail_engine.check_action({"action": tool_name, "params": params})
        if not guardrail_check['allowed']:
            raise PermissionError(f"Action blocked by guardrail: {guardrail_check['violation']}")

        # Execute tool
        result = await tool.execute(**params)

        # Log action
        self.security_guardian.log_action(tool_name, params, result, risk, task_id=task.id, user_id=task.user_id)

        return result

    async def _handle_spawn_command(self, task: Task) -> Dict[str, Any]:
        # Simple parsing for "spawn <role> agent"
        parts = task.description.lower().split()
        role = "assistant"
        if "hacker" in parts: role = "hacker"
        elif "developer" in parts: role = "developer"
        elif "researcher" in parts: role = "researcher"

        agent = await self.spawner.spawn_agent(role, {"description": "Subtask for spawned agent"})
        return {"success": True, "message": f"Spawned {role} agent: {agent.id}", "agent_id": agent.id}

    async def cleanup(self):
        pass
