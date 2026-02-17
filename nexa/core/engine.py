import asyncio
import logging
from nexa.core.task_manager import TaskManager
from nexa.intelligence.router import EnhancedLLMRouter
from nexa.core.security import SecurityGuardian
from nexa.privacy.guardian import PrivacyGuardian
from nexa.core.innovation import InnovationModule
from nexa.interfaces.messaging import MessagingHub
from nexa.memory.soul import SoulFile
from nexa.memory.vector import VectorMemory, TimeCapsule

logger = logging.getLogger(__name__)

class NexaEngine:
    """Main Nexa Bot engine"""

    def __init__(self):
        self.running = False
        self.task_manager = None
        self.llm_router = None
        self.privacy_guardian = PrivacyGuardian()
        self.soul = SoulFile()
        self.memory = VectorMemory()
        self.time_capsule = TimeCapsule(self.memory)
        self.innovation = InnovationModule()
        self.messaging_hub = MessagingHub()
        self.background_tasks = []
        logger.info("Nexa Bot engine initialized")

    async def setup(self):
        """Run the setup wizard"""
        from nexa.interfaces.tui import TUISetupWizard
        wizard = TUISetupWizard()
        await wizard.run()

    async def start(self):
        """Start Nexa Bot"""
        if self.running:
            return
        logger.info("Starting Nexa Bot...")
        self.running = True

        # 1. Initialize DB
        from nexa.core.database import init_db
        await init_db()

        # 2. Load Tools
        from nexa.tools.registry import registry
        await registry.load_default_tools()

        # 3. Initialize components
        self.llm_router = EnhancedLLMRouter()
        self.security_guardian = SecurityGuardian({})
        self.task_manager = TaskManager(self.llm_router, self.security_guardian)

        # 4. Start Privacy monitoring
        await self.privacy_guardian.start_monitoring()

        # 5. Start Messaging interfaces
        await self.messaging_hub.start_all()

        # 6. Start Task processing loop
        self.background_tasks.append(asyncio.create_task(self._task_processing_loop()))

        # 7. Initialize Innovation features
        logger.info("Innovation Module ready.")

        logger.info("Nexa Bot started successfully!")

    async def _task_processing_loop(self):
        """Continuous task processing loop"""
        while self.running:
            try:
                await self.task_manager.process_queue()
                await asyncio.sleep(1) # Prevent busy waiting
            except Exception as e:
                logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(5)

    async def stop(self, level: int = 0):
        """Stop Nexa Bot with optional level"""
        logger.info(f"Stopping Nexa Bot (Level {level})...")
        self.running = False

        if level >= 3:
            # Full system lock or emergency shutdown
            logger.warning("EMERGENCY SHUTDOWN IN PROGRESS")

        # Stop background tasks
        for task in self.background_tasks:
            task.cancel()

        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
            self.background_tasks = []

        if self.task_manager:
            await self.task_manager.cleanup()

        # Stop privacy guardian
        await self.privacy_guardian.stop()

        # Stop messaging interfaces
        await self.messaging_hub.stop_all()

        logger.info("Nexa Bot stopped")

    async def execute_command(self, command: str):
        """Execute a command and wait for result"""
        if not self.task_manager:
            await self.start()

        # Log to long-term memory
        await self.memory.add(f"User command: {command}")

        task = await self.task_manager.create_task_from_command(command)

        # Wait for task completion (polling for simplicity, or use Event)
        from nexa.core.database import AsyncSessionLocal
        from nexa.models.core import Task
        from sqlalchemy import select

        max_wait = 60 # seconds
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < max_wait:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Task).where(Task.id == task.id))
                updated_task = result.scalars().first()
                if updated_task.status in ['completed', 'failed']:
                    # Learn from interaction
                    if updated_task.status == 'completed':
                        self.soul.learn_from_interaction(command, str(updated_task.result), True)
                    return updated_task.result
            await asyncio.sleep(0.5)

        return {"success": False, "error": "Task timed out"}

# Global engine instance for convenience
engine = NexaEngine()
