import asyncio
import logging
from nexa.core.task_manager import TaskManager
from nexa.intelligence.router import EnhancedLLMRouter

logger = logging.getLogger(__name__)

class NexaEngine:
    """Main Nexa Bot engine"""

    def __init__(self):
        self.running = False
        self.task_manager = None
        self.llm_router = None
        logger.info("Nexa Bot engine initialized")

    async def start(self):
        """Start Nexa Bot"""
        logger.info("Starting Nexa Bot...")
        self.running = True

        # Initialize components
        self.llm_router = EnhancedLLMRouter()
        self.task_manager = TaskManager(self.llm_router)

        logger.info("Nexa Bot started successfully!")

        # Run main loop in the background if needed,
        # but for CLI use we might just call it explicitly

    async def stop(self):
        """Stop Nexa Bot"""
        logger.info("Stopping Nexa Bot...")
        self.running = False
        if self.task_manager:
            await self.task_manager.cleanup()
        logger.info("Nexa Bot stopped")

    async def execute_command(self, command: str):
        """Execute a command"""
        if not self.task_manager:
            await self.start()

        task = await self.task_manager.create_task_from_command(command)
        await self.task_manager.process_queue()
        return task.result

# Global engine instance for convenience
engine = NexaEngine()
