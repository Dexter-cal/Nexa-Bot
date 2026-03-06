import asyncio
import logging
from epex.tools.registry import registry

logger = logging.getLogger(__name__)

class VoiceCommandBridge:
    """
    Hands-free voice interface for Epex Bot.
    """
    def __init__(self, engine=None):
        self.engine = engine
        self.active = False

    async def start_listening_loop(self):
        self.active = True
        logger.info("Voice Command Bridge activated.")

        while self.active:
            try:
                # 1. Listen for trigger or command
                stt_tool = registry.get("voice.listen")
                res = await stt_tool.execute(duration=3)

                if res.success and res.output:
                    text = res.output.lower()
                    if "epex" in text:
                        logger.info(f"Voice trigger detected: {text}")
                        # 2. Execute as command
                        clean_cmd = text.replace("epex", "").strip()
                        if clean_cmd:
                            if not self.engine:
                                from epex.core.engine import engine
                                self.engine = engine
                            result = await self.engine.execute_command(clean_cmd)
                            # 3. Speak the result
                            tts_tool = registry.get("voice.speak")
                            await tts_tool.execute(text=result.get('response', "Command processed."))
            except Exception as e:
                logger.error(f"Voice bridge error: {e}")
            await asyncio.sleep(0.5)

    def stop(self):
        self.active = False
        logger.info("Voice Command Bridge deactivated.")
