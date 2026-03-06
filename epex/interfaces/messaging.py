import asyncio
import logging
import os
import json
import aiohttp
from typing import Optional, Dict, Any, List
from epex.intelligence.api_manager import UniversalAPIKeyManager

logger = logging.getLogger(__name__)

class PlatformBridge:
    def __init__(self, name: str):
        self.name = name
        self.running = False

    async def start(self):
        self.running = True
        logger.info(f"{self.name} bridge started")

    async def stop(self):
        self.running = False
        logger.info(f"{self.name} bridge stopped")

    async def send_message(self, text: str, recipient: str = None):
        logger.info(f"[{self.name}] To {recipient or 'All'}: {text}")

class TelegramBridge(PlatformBridge):
    def __init__(self, token: str = None):
        super().__init__("Telegram")
        self.token = token
        self.application = None

    async def start(self):
        if not self.token:
            api_manager = UniversalAPIKeyManager()
            keys = await api_manager.auto_detect_keys()
            # Support multi-account if keys is a list
            t_keys = keys.get('telegram', [])
            self.token = t_keys[0] if isinstance(t_keys, list) and t_keys else t_keys

        if not self.token:
            logger.warning("Telegram token missing. Bridge disabled.")
            return

        try:
            from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
            self.application = ApplicationBuilder().token(self.token).build()
            self.application.add_handler(CommandHandler("start", self._handle_start))
            self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self._handle_message))

            await self.application.initialize()
            await self.application.start_polling()
            self.running = True
            logger.info("Telegram bridge active.")
        except Exception as e:
            logger.error(f"Telegram start error: {e}")

    async def _handle_start(self, update, context):
        await update.message.reply_text("⚡ EPEX BOT active on Telegram. Ready for commands.")

    async def _handle_message(self, update, context):
        from epex.core.engine import engine
        user_text = update.message.text
        result = await engine.execute_command(user_text)
        await update.message.reply_text(result.get('response', "Command processed."))

class DiscordBridge(PlatformBridge):
    def __init__(self, token: str = None):
        super().__init__("Discord")
        self.token = token

    async def start(self):
        if not self.token:
            api_manager = UniversalAPIKeyManager()
            keys = await api_manager.auto_detect_keys()
            d_keys = keys.get('discord', [])
            self.token = d_keys[0] if isinstance(d_keys, list) and d_keys else d_keys

        if not self.token:
             logger.warning("Discord token missing.")
             return

        # Mocking discord implementation
        self.running = True
        logger.info("Discord bridge active (Simulated).")

class WhatsAppBridge(PlatformBridge):
    def __init__(self, api_key: str = None):
        super().__init__("WhatsApp")
        self.api_key = api_key

class SlackBridge(PlatformBridge):
    def __init__(self, token: str = None):
        super().__init__("Slack")
        self.token = token

class TwitterBridge(PlatformBridge):
    def __init__(self):
        super().__init__("Twitter/X")

class MessengerBridge(PlatformBridge):
    def __init__(self):
        super().__init__("FB Messenger")

class WebhookBridge(PlatformBridge):
    def __init__(self):
        super().__init__("Custom Webhooks")

class MessagingHub:
    """
    Central hub for multi-platform communication (9 platforms supported)
    """
    def __init__(self):
        self.bridges: Dict[str, PlatformBridge] = {
            "telegram": TelegramBridge(),
            "discord": DiscordBridge(),
            "slack": SlackBridge(),
            "whatsapp": WhatsAppBridge(),
            "twitter": TwitterBridge(),
            "messenger": MessengerBridge(),
            "webhooks": WebhookBridge(),
            "sms": PlatformBridge("SMS"),
            "email": PlatformBridge("Email")
        }

    async def start_all(self):
        for bridge in self.bridges.values():
            try:
                await bridge.start()
            except Exception as e:
                logger.error(f"Failed to start {bridge.name}: {e}")

    async def stop_all(self):
        for bridge in self.bridges.values():
            await bridge.stop()

    async def notify(self, text: str, recipient: str = None, platforms: List[str] = None):
        """
        Send a notification to one or more platforms
        """
        target_platforms = platforms or ["telegram", "email", "sms"]
        for p in target_platforms:
            if p in self.bridges:
                await self.bridges[p].send_message(text, recipient)

    async def broadcast(self, text: str):
        """
        Broadcast to all active bridges
        """
        for bridge in self.bridges.values():
            if bridge.running:
                await bridge.send_message(text)

# Singleton instance
messaging_hub = MessagingHub()
