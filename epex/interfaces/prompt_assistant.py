import logging
import re
from typing import List, Dict, Any, Optional
from epex.tools.registry import registry

logger = logging.getLogger(__name__)

class PromptAssistant:
    """
    Intelligent logic for command completion and intent detection.
    """
    def __init__(self):
        self.commands = [
            "chat", "setup", "list", "pull", "remove", "clean", "login",
            "logout", "whoami", "config", "server", "disk health",
            "disk analyze", "recover deleted-files", "repair boot",
            "drivers scan", "network diagnose", "wifi optimize",
            "ghost mode", "return report", "visuals"
        ]

    def get_suggestions(self, partial: str) -> List[str]:
        """Fuzzy autocomplete suggestions"""
        if not partial: return []
        partial = partial.lower()
        return [c for c in self.commands if partial in c]

    def detect_intent(self, text: str) -> Optional[str]:
        """Detect intent from natural language if no direct command matches"""
        text = text.lower()
        patterns = {
            "maint.disk_health": [r"disk.*health", r"hard drive.*ok", r"smart data"],
            "maint.analyze_usage": [r"disk.*usage", r"low.*space", r"what.*eating.*storage"],
            "maint.recover_files": [r"recover.*file", r"deleted.*file", r"ransomware"],
            "system.tunnel": [r"tunnel", r"expose.*api", r"ngrok"],
            "network.diagnose": [r"internet.*not working", r"network.*diagnose", r"can't connect"],
        }

        for tool, p_list in patterns.items():
            for p in p_list:
                if re.search(p, text):
                    return tool
        return None

    def auto_fill(self, command: str) -> str:
        """Add smart defaults to common commands"""
        if command == "epex backup":
            return "epex backup --destination ~/.epex/backups/ --exclude node_modules"
        if command == "epex scan":
            return "epex security scan --quick --quarantine"
        return command
