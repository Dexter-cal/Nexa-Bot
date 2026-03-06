import logging
from epex.memory.soul import SoulFile
from epex.intelligence.router import RefusalDetector

logger = logging.getLogger(__name__)

class SentimentAuraManager:
    """
    Manages the 'Aura' of Epex Bot based on user sentiment and interaction history.
    Implements sentiment-driven behavior scaling.
    """

    def __init__(self, soul: SoulFile):
        self.soul = soul
        self.detector = RefusalDetector()

        # Mapping sentiment and keywords to Auras
        self.aura_map = {
            "negative": "empathetic",
            "positive": "friendly",
            "neutral": "professional"
        }

        self.scaling_rules = {
            "aggressive": {"priority": "speed", "tier_limit": 3},
            "professional": {"priority": "quality", "tier_limit": 1},
            "zen": {"priority": "quality", "tier_limit": 1},
            "friendly": {"priority": "balanced", "tier_limit": 2},
            "empathetic": {"priority": "quality", "tier_limit": 1},
            "witty": {"priority": "balanced", "tier_limit": 2}
        }

    async def update_aura_from_input(self, user_input: str):
        """Analyze input sentiment and update Soul File aura"""
        sentiment = self.detector.analyze_sentiment(user_input)

        # Check for specific intent-based aura shifts
        input_lower = user_input.lower()
        new_aura = self.aura_map.get(sentiment, "professional")

        if any(w in input_lower for w in ["hurry", "fast", "quick", "immediately"]):
            new_aura = "aggressive"
        elif any(w in input_lower for w in ["joke", "funny", "laugh"]):
            new_aura = "witty"
        elif any(w in input_lower for w in ["please", "thanks", "thank you", "kindly"]):
            new_aura = "friendly"
        elif any(w in input_lower for w in ["stress", "sad", "angry", "frustrated", "help me"]):
            new_aura = "empathetic"
        elif any(w in input_lower for w in ["meditate", "calm", "relax"]):
            new_aura = "zen"

        old_aura = self.soul.data.get("current_aura")
        if new_aura != old_aura:
            logger.info(f"Aura shift detected: {old_aura} -> {new_aura}")
            self.soul.set_aura(new_aura)
            return True
        return False

    def get_scaling_config(self):
        """Get the auto-scaling configuration for the current aura"""
        aura = self.soul.data.get("current_aura", "professional")
        return self.scaling_rules.get(aura, self.scaling_rules["professional"])
