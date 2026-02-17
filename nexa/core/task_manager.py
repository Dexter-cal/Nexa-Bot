import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from nexa.intelligence.router import EnhancedLLMRouter
from nexa.tools.registry import registry
from nexa.tools.base import ToolResult
from nexa.core.security import SecurityGuardian, GuardrailEngine
from nexa.models.core import Task
from nexa.core.database import AsyncSessionLocal
from nexa.orchestration.spawner import AgentSpawner
from nexa.intelligence.brain import StrategicPlanner
from nexa.intelligence.council import AICouncil
from nexa.features.self_healing import SelfHealingLoop
from nexa.core.modes import ModeManager, NexaMode
from nexa.core.roles import RoleManager

logger = logging.getLogger(__name__)

class TaskManager:
    """
    Manage tasks and their execution with planning and security
    """
    def __init__(self, llm_router=None, security_guardian=None):
        self.llm_router = llm_router or EnhancedLLMRouter()
        self.security_guardian = security_guardian or SecurityGuardian({})
        self.guardrail_engine = GuardrailEngine(llm_router=self.llm_router)
        self.mode_manager = ModeManager()
        self.role_manager = RoleManager()
        self.spawner = AgentSpawner()
        self.planner = StrategicPlanner()
        self.council = AICouncil()
        self.healing_loop = SelfHealingLoop(engine=self.llm_router)
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
        while not self.queue.empty():
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
        # Load Soul context
        from nexa.core.engine import engine
        soul_context = engine.soul.get_summary()

        # 0. Handle simple direct questions/commands
        lower_desc = task.description.lower()
        if any(q in lower_desc for q in ["who created you", "who is your creator", "who made you"]):
             return await self.llm_router.execute(task.description)

        # Support for parallel agent spawning
        if "spawn" in lower_desc and "agent" in lower_desc:
             return await self._handle_spawn_command(task)

        # Mirror-World Simulation command
        if lower_desc.startswith("simulate task"):
             return await self._handle_simulate_command(task)

        # 1. Plan the task using Strategic Planner
        plan = await self.planner.create_plan(f"User context: {soul_context}. Goal: {task.description}")
        task.execution_plan = plan.get('primary_strategy', [])

        if not task.execution_plan and not plan.get('success', True):
            # Fallback to simple planning if strategic planner fails
            simple_plan = await self._plan_task_simple(task)
            task.execution_plan = simple_plan.get('steps', [])

        # 2. Execute steps
        results = []
        for step in (task.execution_plan or []):
            # For critical steps, consult the council
            if task.priority == 'critical' or step.get('risk_level') == 'high':
                approved = await self.council.vote_on_action(step.get('description', 'Unknown action'))
                if not approved:
                    return {"success": False, "error": "Action rejected by AI Council", "step": step}

            result = await self._execute_step(step, task)
            results.append(result.model_dump())
            if not result.success:
                # Try alternative strategy if available
                if plan.get('alternative_strategy'):
                    logger.warning("Primary strategy failed. Attempting alternative strategy...")
                    # Simplified: just log for now
                return {"success": False, "error": result.error, "step_results": results}

        # 3. Aggregate final result
        final_response = await self.llm_router.execute(
            f"Task: {task.description}\nSteps executed: {json.dumps(results)}\nSummarize final result."
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

    async def _execute_step(self, step: Dict[str, Any], task: Task) -> ToolResult:
        tool_name = step.get('tool')
        params = step.get('params', {})

        if self.mode_manager.current_mode == NexaMode.SHADOW:
            logger.info(f"SHADOW MODE: Observing action {tool_name} but not executing.")
            return ToolResult(success=True, output="Shadow mode: Action observed.")

        if not tool_name:
            # Fallback to LLM execution if no tool specified
            res = await self.llm_router.execute(task.description)
            return ToolResult(
                success=res.get('success', False),
                output=res.get('response'),
                error=res.get('reason'),
                metadata={'model': res.get('model')}
            )

        tool = registry.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        # Security & Mode check
        risk = self.security_guardian.assess_risk(tool_name, params)
        if self.mode_manager.should_ask_approval(risk.value):
            logger.info(f"APPROVAL REQUIRED in {self.mode_manager.current_mode.value} mode for {tool_name} (Risk: {risk.value})")
            # In a production environment, this would trigger a UI prompt or mobile notification
            # await alert_manager.emit("Approval Required", f"Action {tool_name} requires your approval in {self.mode_manager.current_mode.value} mode.", severity="high")

        # Role-specific guardrails
        role_guardrails = self.role_manager.get_role_guardrails()
        for rule in role_guardrails:
            await self.guardrail_engine.add_rule(rule)

        guardrail_check = await self.guardrail_engine.check_action({"action": tool_name, "params": params})
        if not guardrail_check['allowed']:
            raise PermissionError(f"Action blocked by guardrail: {guardrail_check['violation']}")

        # Execute tool with self-healing
        result = await self.healing_loop.run_with_healing(tool.execute, **params)

        # Log action
        self.security_guardian.log_action(tool_name, params, result, risk, task_id=task.id, user_id=task.user_id)

        return result

    async def _handle_simulate_command(self, task: Task) -> Dict[str, Any]:
        task_to_sim = task.description[len("simulate task "):].strip()
        plan = await self.planner.create_plan(task_to_sim)

        from nexa.features.mirror_world import MirrorWorldSandbox
        sandbox = MirrorWorldSandbox(self.llm_router)
        report = await sandbox.simulate_task(task_to_sim, plan.get('primary_strategy', []))

        return {"success": True, "response": report, "plan": plan}

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
