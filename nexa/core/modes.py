from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NexaMode(Enum):
    ASSISTIVE = "assistive"
    PARTNER = "partner"
    AUTONOMOUS = "autonomous"
    SHADOW = "shadow"
    COLLABORATIVE = "collaborative"

class ModeManager:
    """
    Manages the current operational mode of Nexa Bot
    """
    def __init__(self, mode: NexaMode = NexaMode.PARTNER):
        self.current_mode = mode

    def set_mode(self, mode: str):
        try:
            self.current_mode = NexaMode(mode.lower())
            logger.info(f"System mode switched to: {self.current_mode.value}")
        except ValueError:
            logger.error(f"Invalid mode: {mode}")

    def get_mode_description(self) -> str:
        descriptions = {
            NexaMode.ASSISTIVE: "Passive. Waits for user commands. No proactive actions.",
            NexaMode.PARTNER: "Proactive. Suggests steps and flags problems. Asks for approval on side effects.",
            NexaMode.AUTONOMOUS: "Fully independent within guardrails. Plans and executes without asking.",
            NexaMode.SHADOW: "Observation only. Learns patterns but never acts.",
            NexaMode.COLLABORATIVE: "Works alongside user in real time. Low-risk actions are automatic."
        }
        return descriptions[self.current_mode]

    def should_ask_approval(self, risk_level: str) -> bool:
        """Determines if approval is needed based on mode and risk"""
        if self.current_mode == NexaMode.AUTONOMOUS:
            return risk_level == "critical"
        if self.current_mode == NexaMode.ASSISTIVE:
            return True # Always ask in assistive mode for anything beyond info
        if self.current_mode == NexaMode.PARTNER:
            return risk_level in ["medium", "high", "critical"]
        if self.current_mode == NexaMode.COLLABORATIVE:
            return risk_level in ["high", "critical"]
        return True
