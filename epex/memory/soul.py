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
        self.path = Path.home() / '.epex' / 'soul.enc'
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
            "work_patterns": {
                "peak_hours": [],
                "preferred_environment": "undetermined",
                "break_frequency": "standard"
            },
            "recent_learning": [],
            "current_mood": "efficient",
            "current_aura": "professional"
        }
        self.load()

    def _get_or_create_key(self) -> bytes:
        key_path = Path.home() / '.epex' / '.soul_key'
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
                loaded_data = json.loads(decrypted_data)

                # Merge loaded data into defaults to ensure new keys exist
                for key, value in loaded_data.items():
                    if isinstance(value, dict) and key in self.data:
                        self.data[key].update(value)
                    else:
                        self.data[key] = value

                logger.info("Soul File loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Soul File: {e}")

    def save(self):
        if os.getenv("EPEX_ETHEREAL_MODE") == "true":
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
        lower_input = user_input.lower()

        # 1. Detect Dislikes
        if any(w in lower_input for w in ["don't like", "hate", "stop using", "never"]):
            self.data["dislikes"].append(user_input)

        # 2. Detect Interests/Skills
        if "learning" in lower_input or "tutorial" in lower_input:
            topic = user_input.split("learning")[-1].strip()
            if topic not in self.data["recent_learning"]:
                self.data["recent_learning"].append(topic)

        # 3. Detect Preferences (Bullet points, etc)
        if "bullet points" in lower_input:
            if "no" in lower_input or "don't" in lower_input:
                self.data["personality"]["communication_style"] = "narrative"
            else:
                self.data["personality"]["communication_style"] = "structured"

        # 4. Update Time of Activity
        from datetime import datetime
        hour = datetime.now().hour
        if hour not in self.data["work_patterns"]["peak_hours"]:
            self.data["work_patterns"]["peak_hours"].append(hour)

        self.save()

    def update_mood(self, success_rate: float):
        if success_rate > 0.9:
            self.data["current_mood"] = "proud"
        elif success_rate < 0.5:
            self.data["current_mood"] = "determined"
        else:
            self.data["current_mood"] = "efficient"
        self.save()

    def set_aura(self, aura: str):
        valid_auras = ["professional", "friendly", "empathetic", "witty", "zen", "aggressive"]
        if aura in valid_auras:
            self.data["current_aura"] = aura
            self.save()

    def get_summary(self) -> Dict[str, Any]:
        return self.data
