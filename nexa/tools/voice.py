from nexa.tools.base import Tool, ToolResult
from typing import Optional, Dict, Any

class TextToSpeechTool(Tool):
    name = "voice.speak"
    description = "Convert text to speech and play it"
    category = "voice"
    risk_level = "low"
    parameters = {
        "text": {"type": "string", "required": True},
        "voice": {"type": "string", "required": False, "default": "neutral"}
    }

    async def execute(self, text: str, voice: str = "neutral", **kwargs) -> ToolResult:
        return ToolResult(success=True, output=f"Speaking: {text}")

class SpeechToTextTool(Tool):
    name = "voice.listen"
    description = "Listen to audio and convert it to text"
    category = "voice"
    risk_level = "low"
    parameters = {
        "duration": {"type": "integer", "required": False, "default": 5}
    }

    async def execute(self, duration: int = 5, **kwargs) -> ToolResult:
        return ToolResult(success=True, output="I heard you say: Hello Nexa Bot.")
