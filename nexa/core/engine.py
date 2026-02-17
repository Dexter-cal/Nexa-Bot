import asyncio
import logging
from nexa.core.task_manager import TaskManager
from nexa.intelligence.router import EnhancedLLMRouter
from nexa.core.security import SecurityGuardian
from nexa.privacy.guardian import PrivacyGuardian
from nexa.core.innovation import InnovationModule

logger = logging.getLogger(__name__)

class NexaEngine:
    """Main Nexa Bot engine"""

    def __init__(self):
        self.running = False
        self.task_manager = None
        self.llm_router = None
        self.privacy_guardian = PrivacyGuardian()
        self.innovation = InnovationModule()
        self.background_tasks = []
        logger.info("Nexa Bot engine initialized")

    async def setup(self):
        """Run the setup wizard"""
        from nexa.interfaces.tui import TUISetupWizard
        wizard = TUISetupWizard()
        await wizard.run()

    async def start(self):
        """Start Nexa Bot"""
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

        # 5. Initialize Innovation features
        logger.info("Innovation Module ready.")

        logger.info("Nexa Bot started successfully!")

        # Run main loop in the background if needed,
        # but for CLI use we might just call it explicitly

    async def stop(self):
        """Stop Nexa Bot"""
        logger.info("Stopping Nexa Bot...")
        self.running = False

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

        logger.info("Nexa Bot stopped")

    async def execute_command(self, command: str):
        """Execute a command"""
        if not self.task_manager:
            await self.start()

        task = await self.task_manager.create_task_from_command(command)
        await self.task_manager.process_queue()

        # Fetch updated task from DB to get the result
        from nexa.core.database import AsyncSessionLocal
        from nexa.models.core import Task
        from sqlalchemy import select
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Task).where(Task.id == task.id))
            updated_task = result.scalars().first()
            return updated_task.result

# Global engine instance for convenience
engine = NexaEngine()
