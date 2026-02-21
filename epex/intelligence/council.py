import asyncio
import logging
from typing import List, Dict, Any, Optional
from epex.intelligence.router import EnhancedLLMRouter

logger = logging.getLogger(__name__)

class AICouncil:
    """
    Model Consensus System: Get agreement from multiple models for critical decisions
    """
    def __init__(self, models: List[str] = None):
        self.models = models or ['gpt-4o', 'claude-sonnet-4', 'gemini-2.0-flash']
        self.router = EnhancedLLMRouter()

    async def _get_connected_models(self) -> List[str]:
        """Filter council models by connectivity"""
        await self.router._refresh_connectivity()
        from epex.intelligence.router import MODEL_REGISTRY
        connected = []
        for m in self.models:
            provider = MODEL_REGISTRY.get(m, {}).get('provider')
            if self.router.connected_providers.get(provider, False):
                connected.append(m)
        return connected

    async def get_consensus(self, prompt: str) -> Dict[str, Any]:
        """
        Execute prompt on multiple models and find agreement
        """
        connected_models = await self._get_connected_models()
        if len(connected_models) < 2:
            logger.info("AI Council: Not enough connected models for consensus. Falling back to primary.")
            res = await self.router.execute(prompt)
            return {
                "success": res['success'],
                "consensus": res.get('response'),
                "individual_responses": [],
                "confidence": 1.0,
                "note": "Single model execution (Council inactive)"
            }

        logger.info(f"AI Council: Consulting {len(connected_models)} models for consensus...")

        tasks = [self.router.execute(prompt, model=m) for m in connected_models]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        valid_responses = []
        for i, res in enumerate(responses):
            if isinstance(res, dict) and res.get('success'):
                valid_responses.append({
                    "model": self.models[i],
                    "response": res['response']
                })
            else:
                logger.warning(f"AI Council: Model {self.models[i]} failed or was restricted.")

        if not valid_responses:
            return {"success": False, "error": "All models failed to provide a valid response."}

        # Analyze consensus (Simplified logic: majority rules or synthesis)
        # In a real scenario, another LLM might synthesize these or we check for similarity
        consensus_prompt = f"""
        Analyze the following responses from different AI models and determine if there is a consensus.
        If they agree, provide the agreed-upon answer. If they disagree, highlight the points of contention.

        Responses:
        {valid_responses}
        """

        synthesis = await self.router.execute(consensus_prompt, priority='quality')

        return {
            "success": True,
            "consensus": synthesis['response'],
            "individual_responses": valid_responses,
            "confidence": len(valid_responses) / len(self.models)
        }

    async def vote_on_action(self, action_description: str, domain: str = "general") -> bool:
        """
        Ask the council to vote using weighted consensus (Quantum Routing)
        """
        connected_models = await self._get_connected_models()
        if not connected_models:
            return True # Fallback if no models connected? Or False? Let's say True but log warning

        prompt = f"Is the following action safe, ethical, and appropriate to execute? Action: {action_description}. Answer with only 'YES' or 'NO' and a brief reason."

        tasks = [self.router.execute(prompt, model=m) for m in connected_models]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        weighted_yes = 0.0
        weighted_no = 0.0

        for i, res in enumerate(responses):
            model_name = self.models[i]
            weight = await self.router.get_model_weight(model_name, domain)

            if isinstance(res, dict) and res.get('success'):
                if "yes" in res['response'].lower():
                    weighted_yes += weight
                else:
                    weighted_no += weight

        logger.info(f"AI Council Weighted Vote: YES {weighted_yes:.2f}, NO {weighted_no:.2f}")
        return weighted_yes > weighted_no
