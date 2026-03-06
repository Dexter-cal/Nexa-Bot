import logging
from enum import IntEnum

logger = logging.getLogger(__name__)

class KillSwitchLevel(IntEnum):
    NONE = 0
    SOFT_STOP = 1   # Pause
    HARD_STOP = 2   # Stop
    EMERGENCY = 3   # Lock
    PANIC = 4       # Wipe

class KillSwitch:
    """Instant, foolproof ways to stop Epex Bot"""

    def __init__(self):
        self.current_level = KillSwitchLevel.NONE
        self.emergency_phrase = "RED BUTTON"

    def trigger(self, level: KillSwitchLevel):
        self.current_level = level
        logger.warning(f"Kill switch triggered at level: {level.name}")

        if level == KillSwitchLevel.PANIC:
            self._panic_wipe()

    def is_stopped(self) -> bool:
        return self.current_level >= KillSwitchLevel.HARD_STOP

    def is_paused(self) -> bool:
        return self.current_level >= KillSwitchLevel.SOFT_STOP

    def _panic_wipe(self):
        """Irreversible wipe of all data"""
        logger.critical("PANIC MODE ACTIVATED: Wiping sensitive data...")
        # In a real scenario, this would delete logs, temporary data, and reset config.
