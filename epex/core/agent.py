import time
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import psutil
import logging

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    SPAWNING = "spawning"
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"

class Agent:
    """
    Base agent class - can be spawned and run independently
    """

    def __init__(
        self,
        agent_id: str,
        role: str,
        mode: str,
        parent_id: Optional[str] = None
    ):
        self.id = agent_id
        self.role = role
        self.mode = mode
        self.parent_id = parent_id

        # State
        self.status = AgentStatus.SPAWNING
        self.current_task = None
        self.task_queue = asyncio.Queue()

        # Resources
        self.cpu_usage = 0.0
        self.memory_usage = 0.0

        # Communication
        self.message_queue = asyncio.Queue()

        # Timestamps
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None

        # Results
        self.results = []
        self.errors = []

        # Execution
        self._running = False
        self._main_task = None

    async def start(self, initial_task: Optional[Dict] = None):
        """
        Start the agent
        """
        from epex.intelligence.router import EnhancedLLMRouter
        self.llm_router = EnhancedLLMRouter()

        self.status = AgentStatus.RUNNING
        self.started_at = datetime.now()
        self._running = True

        # Start main loop
        self._main_task = asyncio.create_task(self._main_loop())

        # Add initial task if provided
        if initial_task:
            await self.add_task(initial_task)

        return self

    async def _main_loop(self):
        """
        Main agent execution loop
        """
        while self._running:
            try:
                # Check for messages
                await self._process_messages()

                # Get next task
                if not self.task_queue.empty():
                    task = await self.task_queue.get()

                    # Execute task
                    result = await self._execute_task(task)

                    # Store result
                    self.results.append(result)

                    # Mark task done
                    self.task_queue.task_done()
                else:
                    # Idle - wait a bit
                    self.status = AgentStatus.IDLE
                    await asyncio.sleep(0.5)

                # Update resource usage
                await self._update_resources()

            except Exception as e:
                self.errors.append({
                    'error': str(e),
                    'timestamp': datetime.now()
                })
                await asyncio.sleep(1)

    async def _execute_task(self, task: Dict) -> Dict:
        """
        Execute a single task
        """
        self.status = AgentStatus.RUNNING
        self.current_task = task

        prompt = task.get('prompt') or task.get('description')

        try:
            # Simple execution for now, role-based logic can be added here
            response = await self.llm_router.execute(
                prompt=prompt,
                model=task.get('model'),
                priority=task.get('priority', 'balanced')
            )

            return {
                'success': True,
                'task_id': task.get('id'),
                'result': response,
                'agent_id': self.id,
                'completed_at': datetime.now()
            }
        except Exception as e:
            return {
                'success': False,
                'task_id': task.get('id'),
                'error': str(e),
                'agent_id': self.id,
                'failed_at': datetime.now()
            }
        finally:
            self.current_task = None

    async def add_task(self, task: Dict):
        """
        Add task to queue
        """
        if 'id' not in task:
            task['id'] = f"task_{uuid.uuid4().hex[:8]}"
        await self.task_queue.put(task)

    async def _process_messages(self):
        while not self.message_queue.empty():
            message = await self.message_queue.get()
            msg_type = message.get('type')
            if msg_type == 'terminate':
                await self.terminate()

    async def _update_resources(self):
        try:
            process = psutil.Process()
            self.cpu_usage = process.cpu_percent()
            self.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except:
            pass

    async def wait(self):
        await self.task_queue.join()
        self.status = AgentStatus.COMPLETED
        self.completed_at = datetime.now()
        return self.results

    async def terminate(self):
        self._running = False
        self.status = AgentStatus.TERMINATED
        if self._main_task:
            self._main_task.cancel()
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'role': self.role,
            'mode': self.mode,
            'status': self.status.value,
            'parent_id': self.parent_id,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'tasks_completed': len(self.results),
            'created_at': self.created_at.isoformat()
        }
