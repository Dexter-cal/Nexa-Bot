import asyncio
import logging
import os
from typing import Optional, Dict, Any
from nexa.intelligence.api_manager import UniversalAPIKeyManager

logger = logging.getLogger(__name__)

class TelegramInterface:
    """
    Telegram Bot interface for Nexa Bot
    """
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.application = None
        self.running = False

    async def start(self):
        if not self.token:
            # Try to get from API manager
            api_manager = UniversalAPIKeyManager()
            keys = await api_manager.auto_detect_keys()
            self.token = keys.get('telegram')

        if not self.token:
            logger.warning("Telegram token not found. Interface disabled.")
            return

        try:
            from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

            self.application = ApplicationBuilder().token(self.token).build()

            # Add handlers
            self.application.add_handler(CommandHandler("start", self._start_handler))
            self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self._message_handler))

            await self.application.initialize()
            await self.application.start_polling()

            self.running = True
            logger.info("Telegram interface started")
        except Exception as e:
            logger.error(f"Failed to start Telegram interface: {e}")

    async def stop(self):
        if self.application:
            await self.application.stop()
            self.running = False
            logger.info("Telegram interface stopped")

    async def _start_handler(self, update, context):
        await update.message.reply_text("👋 Hello! I'm Nexa Bot. Send me a command or ask a question.")

    async def _message_handler(self, update, context):
        text = update.message.text
        logger.info(f"Received Telegram command: {text}")

        # Send typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Execute command via engine
        from nexa.core.engine import engine
        result = await engine.execute_command(text)

        if result['success']:
            response = result['response']
        else:
            response = f"❌ Error: {result.get('error', 'Unknown error')}"

        await update.message.reply_text(response)

class EmailInterface:
    """
    Email interface (IMAP) for Nexa Bot
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.running = False
        self._task = None

    async def start(self):
        if not self.config.get('email'):
            # Placeholder for config loading
            return

        self.running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Email interface started")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
        logger.info("Email interface stopped")

    async def _poll_loop(self):
        while self.running:
            try:
                # Mock IMAP polling
                # In real implementation, use imaplib or aioimaplib
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Email poll error: {e}")
                await asyncio.sleep(60)

class MessagingHub:
    """
    Coordinator for all messaging interfaces
    """
    def __init__(self):
        self.telegram = TelegramInterface()
        self.email = EmailInterface()

    async def start_all(self):
        await self.telegram.start()
        await self.email.start()

    async def stop_all(self):
        await self.telegram.stop()
        await self.email.stop()
