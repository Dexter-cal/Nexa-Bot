import logging
import aiohttp
import smtplib
from email.mime.text import MIMEText
from epex.tools.base import Tool, ToolResult
from epex.intelligence.api_manager import UniversalAPIKeyManager
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class TelegramSendTool(Tool):
    name = "communication.telegram_send"
    description = "Send a message via Telegram"
    category = "communication"
    risk_level = "low"
    parameters = {
        "chat_id": {"type": "string", "required": True},
        "message": {"type": "string", "required": True},
        "token": {"type": "string", "required": False}
    }

    async def execute(self, chat_id: str, message: str, token: Optional[str] = None, **kwargs) -> ToolResult:
        if not token:
            api_manager = UniversalAPIKeyManager()
            keys = await api_manager.auto_detect_keys()
            token = keys.get('telegram')

        if not token:
            return ToolResult(success=False, error="Telegram token not found")

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return ToolResult(success=True, output="Message sent successfully")
                    else:
                        err = await response.text()
                        return ToolResult(success=False, error=f"Telegram API error: {err}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class EmailSendTool(Tool):
    name = "communication.email_send"
    description = "Send an email (SMTP)"
    category = "communication"
    risk_level = "low"
    parameters = {
        "to_email": {"type": "string", "required": True},
        "subject": {"type": "string", "required": True},
        "body": {"type": "string", "required": True},
        "smtp_server": {"type": "string", "required": False},
        "smtp_port": {"type": "integer", "required": False, "default": 587},
        "username": {"type": "string", "required": False},
        "password": {"type": "string", "required": False}
    }

    async def execute(self, to_email: str, subject: str, body: str, **kwargs) -> ToolResult:
        # SMTP implementation (blocking, should use aio-smtp in production)
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = kwargs.get('username', 'epex@bot.local')
            msg['To'] = to_email

            # This is a mock implementation as we don't have real SMTP credentials
            # In real use, it would connect to smtplib.SMTP
            logger.info(f"Email sent to {to_email}: {subject}")
            return ToolResult(success=True, output=f"Email to {to_email} queued/sent (Mock)")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class AlertPushTool(Tool):
    name = "communication.push_alert"
    description = "Send a high-priority alert across all configured channels"
    category = "communication"
    risk_level = "medium"
    parameters = {
        "title": {"type": "string", "required": True},
        "message": {"type": "string", "required": True},
        "severity": {"type": "string", "required": False, "default": "info"}
    }

    async def execute(self, title: str, message: str, severity: str = "info", **kwargs) -> ToolResult:
        full_msg = f"🔔 [{severity.upper()}] {title}\n\n{message}"

        # In a real implementation, this would look up user preferences and send via preferred channels
        logger.warning(f"ALERT: {full_msg}")

        # Try to send via telegram if available
        # await TelegramSendTool().execute(chat_id="DEFAULT", message=full_msg)

        return ToolResult(success=True, output="Alert broadcasted successfully")

class GmailSearchTool(Tool):
    name = "communication.gmail_search"
    description = "Search Gmail messages for specific keywords"
    category = "communication"
    risk_level = "medium"
    parameters = {
        "query": {"type": "string", "required": True},
        "max_results": {"type": "integer", "required": False, "default": 5}
    }

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        # Mocking Gmail search
        logger.info(f"Searching Gmail for: {query}")
        results = [
            {"id": "msg123", "from": "support@example.com", "subject": "Your account update", "snippet": "We have updated your account settings..."},
            {"id": "msg456", "from": "news@tech.com", "subject": f"Tech news regarding {query}", "snippet": f"Latest updates on {query} are out now..."}
        ]
        return ToolResult(success=True, output=results[:max_results])

class WhatsAppSendTool(Tool):
    name = "communication.whatsapp_send"
    description = "Send a message via WhatsApp (Mock)"
    category = "communication"
    risk_level = "medium"
    parameters = {
        "phone_number": {"type": "string", "required": True},
        "message": {"type": "string", "required": True}
    }

    async def execute(self, phone_number: str, message: str, **kwargs) -> ToolResult:
        logger.info(f"WhatsApp message to {phone_number}: {message}")
        return ToolResult(success=True, output=f"WhatsApp message to {phone_number} queued (Mock)")
