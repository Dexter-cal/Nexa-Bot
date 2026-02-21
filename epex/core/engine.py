import asyncio
import logging
import os
from typing import List
from epex.core.task_manager import TaskManager
from epex.intelligence.router import EnhancedLLMRouter
from epex.core.security import SecurityGuardian
from epex.privacy.guardian import PrivacyGuardian
from epex.core.innovation import InnovationModule
from epex.interfaces.messaging import MessagingHub
from epex.memory.soul import SoulFile
from epex.memory.vector import VectorMemory, TimeCapsule
from epex.core.neural_sync import NeuralSync
from epex.interfaces.voice import VoiceCommandBridge

logger = logging.getLogger(__name__)

class EpexEngine:
    """Main Epex Bot engine"""

    def __init__(self):
        self.running = False
        self.task_manager = None
        self.llm_router = None
        self.privacy_guardian = PrivacyGuardian()
        self.soul = SoulFile()
        self.memory = VectorMemory()
        self.time_capsule = TimeCapsule(self.memory)
        self.neural_sync = NeuralSync()
        self.innovation = InnovationModule()
        self.messaging_hub = MessagingHub()
        self.voice_bridge = VoiceCommandBridge(engine=self)
        self.background_tasks = []
        logger.info("Epex Bot engine initialized")

    async def setup(self):
        """Run the setup wizard"""
        from epex.interfaces.tui import TUISetupWizard
        wizard = TUISetupWizard()
        await wizard.run()

    async def start(self):
        """Start Epex Bot"""
        if self.running:
            return
        logger.info("Starting Epex Bot...")
        self.running = True

        # 1. Initialize DB
        from epex.core.database import init_db
        await init_db()

        # 2. Load Tools
        from epex.tools.registry import registry
        await registry.load_default_tools()

        # 3. Initialize components
        self.llm_router = EnhancedLLMRouter()
        self.security_guardian = SecurityGuardian({}, neural_sync=self.neural_sync)
        self.llm_router.aegis = self.security_guardian.aegis
        self.task_manager = TaskManager(self.llm_router, self.security_guardian, soul=self.soul)

        # 4. Start Privacy monitoring
        await self.privacy_guardian.start_monitoring()

        # 5. Start Neural Sync
        await self.neural_sync.start()

        # 6. Start Messaging interfaces
        await self.messaging_hub.start_all()

        # Check for Return Reports on startup
        from epex.foundation.storage import SecureConfigStorage
        storage = SecureConfigStorage()
        config = await storage.load_config()
        if config.get('return_reports'):
            logger.info("Found pending Return Reports. Notification sent.")
            await self.messaging_hub.broadcast(f"Welcome back, {config.get('user_name', 'User')}! I have completed background tasks for you. Ask for a 'return report' to see what I did.")

        # 6. Start Task processing loop
        self.background_tasks.append(asyncio.create_task(self._task_processing_loop()))

        # 7. Initialize Innovation features
        logger.info("Innovation Module ready.")

        logger.info("Epex Bot started successfully!")

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
        """Stop Epex Bot with optional level"""
        logger.info(f"Stopping Epex Bot (Level {level})...")
        self.voice_bridge.stop()

        if level == 1:
            # Level 1: Stop current task only
            # In a real app, we'd need a way to identify and cancel specific tasks
            logger.info("Level 1 Kill: Stopping current task.")
            return

        if level == 2:
            # Level 2: Pause all active agents
            logger.info("Level 2 Kill: Pausing all active agents.")
            if self.task_manager:
                from epex.core.agent import AgentStatus
                for agent in self.task_manager.spawner.spawned_agents.values():
                    agent.status = AgentStatus.PAUSED
            return

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

        # Stop neural sync
        await self.neural_sync.stop()

        # Stop messaging interfaces
        await self.messaging_hub.stop_all()

        logger.info("Epex Bot stopped")

    async def execute_command(self, command: str, attachments: List[str] = None):
        """Execute a command and wait for result"""
        if not self.task_manager:
            await self.start()

        # Handle attachments if any
        attachment_context = ""
        if attachments:
            for path in attachments:
                ext = os.path.splitext(path)[1].lower()
                if ext in ['.pdf', '.docx', '.txt', '.py', '.md']:
                    from epex.tools.registry import registry
                    tool = registry.get("document.parse")
                    res = await tool.execute(path)
                    if res.success:
                        attachment_context += f"\n[ATTACHMENT: {path}]\n{res.output['content']}\n"
                elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    from epex.tools.registry import registry
                    tool = registry.get("vision.analyze_attachment")
                    res = await tool.execute(path)
                    if res.success:
                        attachment_context += f"\n[IMAGE ANALYSIS: {path}]\n{res.output['analysis']}\n"

        if attachment_context:
            command = f"Context from attachments: {attachment_context}\n\nTask: {command}"

        # Load personalization
        config = await self.messaging_hub.bridges['telegram'].api_manager.vault.load_config() if hasattr(self.messaging_hub.bridges['telegram'], 'api_manager') else {}
        # Or better from SecureConfigStorage
        from epex.foundation.storage import SecureConfigStorage
        storage = SecureConfigStorage()
        config = await storage.load_config()

        user_name = config.get('user_name', 'User')
        epex_name = config.get('epex_name', 'Epex')

        # Custom Greeting logic
        if command.lower().strip() in ["hi", "hello", "hey"]:
            greeting = f"hi {user_name}, how is your day? would you like me to help you with something?"
            if user_name == "Max": # Specific requirement check
                 greeting = f"hi sir, how is your day? would you like me to help you with something?"
            return {"success": True, "response": greeting}

        if "my name is" in command.lower():
            new_name = command.lower().split("my name is")[-1].strip().capitalize()
            config['user_name'] = new_name
            await storage.store_config(config)
            return {"success": True, "response": f"hi {new_name}, how can I help you today?"}

        if "create a tool" in command.lower() or "build a tool" in command.lower():
            command = f"Generate a spec and build a tool for: {command}"

        if "ghost mode" in command.lower() or "run in background" in command.lower():
            task = await self.task_manager.create_task_from_command(command.replace("ghost mode", "").replace("run in background", "").strip())
            self.task_manager.shadow_tasks.append(task.id)
            return {"success": True, "response": f"Ghost Mode Activated. I will continue working on '{task.description}' in the background. See you when you return!"}

        if "return report" in command.lower() or "what did i miss" in command.lower():
            reports = config.get('return_reports', [])
            if not reports:
                return {"success": True, "response": "You haven't missed anything! No background tasks have completed since your last check."}

            report_text = "# 📋 EPEX RETURN REPORT\n\nWhile you were away, I completed the following tasks:\n\n"
            for r in reports:
                report_text += f"### 🔹 {r['task_description']}\n- **Summary**: {r['summary']}\n- **Time**: {r['timestamp']}\n\n"

            # Clear reports after showing
            config['return_reports'] = []
            await storage.store_config(config)
            return {"success": True, "response": report_text}

        # Network Delegation
        if command.lower().startswith("ask ") or command.lower().startswith("delegate "):
            parts = command.split()
            peer_name = parts[1]
            remote_cmd = " ".join(parts[2:])
            from epex.core.network_node import network_node
            await network_node.load_peers()
            try:
                res = await network_node.delegate_task(peer_name, remote_cmd)
                return {"success": True, "response": f"🤖 {peer_name} says:\n{res.get('response', 'Task initiated.')}"}
            except Exception as e:
                return {"success": False, "error": f"Failed to communicate with {peer_name}: {e}"}

        # Log to long-term memory
        await self.memory.add(f"User ({user_name}) command: {command}")

        task = await self.task_manager.create_task_from_command(command)

        # Wait for task completion (polling for simplicity, or use Event)
        from epex.core.database import AsyncSessionLocal
        from epex.models.core import Task
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
engine = EpexEngine()
