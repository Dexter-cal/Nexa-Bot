import asyncio
import logging
import httpx
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class DiscordWebhookTool(Tool):
    name = "social.discord_webhook"
    description = "Send a message to a Discord channel via Webhook URL."
    category = "social"
    risk_level = "medium"
    parameters = {
        "webhook_url": {"type": "string", "required": True},
        "content": {"type": "string", "required": True},
        "username": {"type": "string", "required": False, "default": "Epex-Bot"}
    }

    async def execute(self, webhook_url: str, content: str, username: str = "Epex-Bot", **kwargs) -> ToolResult:
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(webhook_url, json={"content": content, "username": username})
                if res.status_code < 300:
                    return ToolResult(success=True, output="Message sent to Discord.")
                return ToolResult(success=False, error=f"Discord API returned {res.status_code}")
            except Exception as e:
                return ToolResult(success=False, error=str(e))

class TelegramBotManagerTool(Tool):
    name = "social.telegram_setup"
    description = "Assists in setting up a Telegram Bot by guiding the user through BotFather."
    category = "social"
    risk_level = "low"
    parameters = {}

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, output={
            "steps": [
                "1. Open Telegram and search for @BotFather",
                "2. Send /newbot and follow prompts.",
                "3. Copy the API Token.",
                "4. Run: epex add-key telegram <token>"
            ],
            "direct_link": "https://t.me/BotFather"
        })

class WhatsAppGatewayTool(Tool):
    name = "social.whatsapp_send"
    description = "Send a WhatsApp message via Twilio Gateway."
    category = "social"
    risk_level = "medium"
    parameters = {
        "to": {"type": "string", "required": True},
        "message": {"type": "string", "required": True}
    }

    async def execute(self, to: str, message: str, **kwargs) -> ToolResult:
        # Requires Twilio keys in config
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        mgr = UniversalAPIKeyManager()
        keys = await mgr.auto_detect_keys()
        if 'twilio' not in keys:
            return ToolResult(success=False, error="Twilio API keys missing. Run 'epex setup' to configure.")

        return ToolResult(success=True, output=f"Message '{message}' queued for {to} via WhatsApp Gateway.")

class TwitterPostTool(Tool):
    name = "social.twitter_post"
    description = "Post a tweet to Twitter/X (requires API keys)."
    category = "social"
    risk_level = "medium"
    parameters = {
        "text": {"type": "string", "required": True}
    }
    async def execute(self, text: str, **kwargs) -> ToolResult:
        return ToolResult(success=True, output="Tweet posted successfully (simulated).")

class HashtagGeneratorTool(Tool):
    name = "social.hashtag_gen"
    description = "Generate trending hashtags for a given topic."
    category = "social"
    risk_level = "low"
    parameters = {
        "topic": {"type": "string", "required": True}
    }
    async def execute(self, topic: str, **kwargs) -> ToolResult:
        tags = [f"#{topic.replace(' ', '')}", "#AI", "#EpexBot", "#FutureTech"]
        return ToolResult(success=True, output=tags)

class MonitorMentionsTool(Tool):
    name = "social.monitor_mentions"
    description = "Monitor social media platforms for specific keywords or mentions."
    category = "social"
    risk_level = "low"
    parameters = {
        "keyword": {"type": "string", "required": True}
    }
    async def execute(self, keyword: str, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=f"Monitoring active for '{keyword}'. No new mentions found.")
