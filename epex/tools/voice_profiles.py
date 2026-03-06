import logging
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult
from epex.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class VoiceProfileTool(Tool):
    name = "voice.set_profile"
    description = "Configure the TTS voice profile, including ElevenLabs clones and emotional tone."
    category = "voice"
    risk_level = "low"
    parameters = {
        "voice_id": {"type": "string", "required": True, "description": "The unique ID of the voice from ElevenLabs."},
        "stability": {"type": "float", "required": False, "default": 0.5},
        "similarity_boost": {"type": "float", "required": False, "default": 0.75}
    }

    async def execute(self, voice_id: str, stability: float = 0.5, similarity_boost: float = 0.75, **kwargs) -> ToolResult:
        storage = SecureConfigStorage()
        config = await storage.load_config()

        voice_config = config.get('voice_settings', {})
        voice_config.update({
            "active_voice_id": voice_id,
            "stability": stability,
            "similarity_boost": similarity_boost
        })

        config['voice_settings'] = voice_config
        await storage.store_config(config)

        logger.info(f"🎙️ VOICE BRIDGE: Profile updated to {voice_id}")
        return ToolResult(success=True, output=f"Voice profile updated to '{voice_id}'. Stability: {stability}, Boost: {similarity_boost}")

class ListVoicesTool(Tool):
    name = "voice.list_profiles"
    description = "List available ElevenLabs voice profiles and clones."
    category = "voice"
    risk_level = "low"
    parameters = {}

    async def execute(self, **kwargs) -> ToolResult:
        # In a real app, this would call ElevenLabs /v1/voices
        mock_voices = [
            {"name": "Epex Prime", "id": "epex_p_01", "type": "cloned"},
            {"name": "Concise Logic", "id": "logic_02", "type": "premade"},
            {"name": "Empathetic Assistant", "id": "emp_03", "type": "premade"}
        ]
        return ToolResult(success=True, output=mock_voices)
