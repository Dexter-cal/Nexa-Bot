import asyncio
import logging
from nexa.intelligence.router import EnhancedLLMRouter

logger = logging.getLogger(__name__)

class Task:
    def __init__(self, description, priority="medium"):
        self.description = description
        self.priority = priority
        self.status = "pending"
        self.result = None

class TaskManager:
    """
    Manage tasks and their execution
    """
    def __init__(self, llm_router=None, tool_registry=None):
        self.llm_router = llm_router or EnhancedLLMRouter()
        self.tool_registry = tool_registry
        self.queue = asyncio.Queue()
        self.active_tasks = []

    async def create_task_from_command(self, command: str):
        task = Task(command)
        await self.queue.put(task)
        return task

    async def process_queue(self):
        if self.queue.empty():
            return

        task = await self.queue.get()
        task.status = "running"
        self.active_tasks.append(task)

        try:
            task.result = await self.execute_task(task)
            task.status = "completed"
        except Exception as e:
            logger.error(f"Task failed: {e}")
            task.status = "failed"
            task.result = str(e)
        finally:
            self.active_tasks.remove(task)

    async def execute_task(self, task: Task):
        # In a real scenario, this would involve planning and tool use
        # For now, we use the LLM router directly
        return await self.llm_router.execute(task.description)

    async def cleanup(self):
        pass
