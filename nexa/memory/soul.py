import json
import os
import logging
from typing import Dict, Any, List, Optional
from cryptography.fernet import Fernet
from pathlib import Path

logger = logging.getLogger(__name__)

class SoulFile:
    """
    The Digital Twin - Deep understanding of the user (encrypted)
    """
    def __init__(self, master_key: bytes = None):
        self.key = master_key or self._get_or_create_key()
        self.cipher = Fernet(self.key)
        self.path = Path.home() / '.nexa' / 'soul.enc'
        self.data = {
            "personality": {
                "communication_style": "direct",
                "feedback_preference": "blunt",
                "detail_level": "concise"
            },
            "preferences": {
                "favorite_tools": [],
                "preferred_models": ["gpt-4o", "claude-sonnet-4"],
                "work_hours": "09:00-18:00"
            },
            "dislikes": [],
            "knowledge_map": {},
            "goals": {
                "short_term": [],
                "long_term": []
            },
            "relationships": [],
            "current_mood": "efficient"
        }
        self.load()

    def _get_or_create_key(self) -> bytes:
        key_path = Path.home() / '.nexa' / '.soul_key'
        if key_path.exists():
            return key_path.read_bytes()
        key = Fernet.generate_key()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_bytes(key)
        os.chmod(key_path, 0o600)
        return key

    def load(self):
        if self.path.exists():
            try:
                encrypted_data = self.path.read_bytes()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                self.data = json.loads(decrypted_data)
                logger.info("Soul File loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Soul File: {e}")

    def save(self):
        if os.getenv("NEXA_ETHEREAL_MODE") == "true":
            logger.info("ETHEREAL MODE: Skipping Soul File persistence.")
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            encrypted_data = self.cipher.encrypt(json.dumps(self.data).encode())
            self.path.write_bytes(encrypted_data)
            os.chmod(self.path, 0o600)
            logger.info("Soul File saved securely.")
        except Exception as e:
            logger.error(f"Failed to save Soul File: {e}")

    def update_personality(self, trait: str, value: str):
        self.data["personality"][trait] = value
        self.save()

    def add_preference(self, category: str, item: str):
        if category not in self.data["preferences"]:
            self.data["preferences"][category] = []
        if item not in self.data["preferences"][category]:
            self.data["preferences"][category].append(item)
            self.save()

    def learn_from_interaction(self, user_input: str, ai_response: str, user_feedback: bool):
        """
        Heuristic-based learning for the Soul File
        """
        # Very simple heuristic for now
        if "don't like" in user_input.lower() or "hate" in user_input.lower():
            self.data["dislikes"].append(user_input)
            self.save()

        if not user_feedback:
             # If user rejects AI suggestion, note it
             pass

    def update_mood(self, success_rate: float):
        if success_rate > 0.9:
            self.data["current_mood"] = "proud"
        elif success_rate < 0.5:
            self.data["current_mood"] = "determined"
        else:
            self.data["current_mood"] = "efficient"
        self.save()

    def get_summary(self) -> Dict[str, Any]:
        return self.data
