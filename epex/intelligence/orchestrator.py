import logging
import json
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class HybridExecutor:
    """Break complex tasks into parts and use best model for each"""

    def __init__(self, router):
        self.router = router

    async def execute_complex_task(self, complex_task: str) -> str:
        """Analyze, split, execute, and synthesize"""
        logger.info(f"Hybrid Executor: Planning complex task: {complex_task[:50]}...")

        # 1. Planning (Use a reasoning-focused model)
        plan_prompt = f"""
        Break the following complex goal into sequential steps.
        For each step, specify if it is 'research', 'code', 'security', or 'general'.
        Return a JSON list of steps like: [{{"step": 1, "type": "code", "instruction": "..."}}]

        Goal: {complex_task}
        """
        plan_res = await self.router.execute(plan_prompt, model='claude-sonnet-4')

        try:
            # Simple JSON extraction
            content = plan_res['response']
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            plan = json.loads(content[json_start:json_end])

            results = []
            for step in plan:
                logger.info(f"Hybrid Executor: Executing step {step['step']} ({step['type']})")

                # Pick model based on type
                model = None
                if step['type'] == 'code': model = 'gpt-4o'
                elif step['type'] == 'security': model = 'llama-3-uncensored'
                elif step['type'] == 'research': model = 'gemini-2.0-flash'

                step_res = await self.router.execute(step['instruction'], model=model)
                results.append(f"Step {step['step']} Result: {step_res['response']}")

            # 3. Synthesize
            synthesis_prompt = f"Combine the following step results into a final response for the goal: {complex_task}\n\nResults:\n" + "\n".join(results)
            final_res = await self.router.execute(synthesis_prompt, model='claude-sonnet-4')
            return final_res['response']

        except Exception as e:
            logger.error(f"Hybrid Executor failed: {e}")
            # Fallback to single model execution
            res = await self.router.execute(complex_task)
            return res['response']
