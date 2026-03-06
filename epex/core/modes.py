import time
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EpexMode(Enum):
    ASSISTIVE = "assistive"
    PARTNER = "partner"
    AUTONOMOUS = "autonomous"
    SHADOW = "shadow"
    COLLABORATIVE = "collaborative"
    ETHEREAL = "ethereal"

class ModeManager:
    """
    Manages the current operational mode of Epex Bot
    """
    def __init__(self, mode: EpexMode = EpexMode.PARTNER):
        self.current_mode = mode

    def set_mode(self, mode: str):
        try:
            self.current_mode = EpexMode(mode.lower())
            logger.info(f"System mode switched to: {self.current_mode.value}")
        except ValueError:
            logger.error(f"Invalid mode: {mode}")

    def get_mode_description(self) -> str:
        descriptions = {
            EpexMode.ASSISTIVE: "Passive. Waits for user commands. No proactive actions.",
            EpexMode.PARTNER: "Proactive. Suggests steps and flags problems. Asks for approval on side effects.",
            EpexMode.AUTONOMOUS: "Fully independent within guardrails. Plans and executes without asking.",
            EpexMode.SHADOW: "Observation only. Learns patterns but never acts.",
            EpexMode.COLLABORATIVE: "Works alongside user in real time. Low-risk actions are automatic.",
            EpexMode.ETHEREAL: "RAM-only execution. No data is written to disk. Maximum privacy."
        }
        return descriptions[self.current_mode]

    def should_ask_approval(self, risk_level: str) -> bool:
        """Determines if approval is needed based on mode and risk"""
        if self.current_mode == EpexMode.AUTONOMOUS:
            return risk_level == "critical"
        if self.current_mode == EpexMode.ASSISTIVE:
            return True # Always ask in assistive mode for anything beyond info
        if self.current_mode == EpexMode.PARTNER:
            return risk_level in ["medium", "high", "critical"]
        if self.current_mode == EpexMode.COLLABORATIVE:
            return risk_level in ["high", "critical"]
        return True
