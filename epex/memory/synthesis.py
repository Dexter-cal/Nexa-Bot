import logging
import json
import datetime
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult
from epex.core.database import AsyncSessionLocal
from sqlalchemy import select

logger = logging.getLogger(__name__)

class MemorySynthesisTool(Tool):
    name = "memory.synthesize_experiences"
    description = "Compress aging memories into high-level summaries to maintain context efficiency and update the Soul File."
    category = "memory"
    risk_level = "low"
    parameters = {
        "days_back": {"type": "integer", "required": False, "default": 7}
    }

    async def execute(self, days_back: int = 7, **kwargs) -> ToolResult:
        from epex.core.engine import engine
        memory = engine.memory
        soul = engine.soul

        now = datetime.datetime.now()
        threshold = now - datetime.timedelta(days=days_back)

        relevant_memories = [
            m for m in memory.store
            if datetime.datetime.fromisoformat(m["timestamp"]) < threshold
            and not m.get("metadata", {}).get("synthesized", False)
        ]

        if not relevant_memories:
            return ToolResult(success=True, output="No aging memories requiring synthesis.")

        # Group by topic or just aggregate
        text_to_summarize = "\n".join([f"- {m['text']}" for m in relevant_memories])

        prompt = f"""
        Summarize the following interaction history into a concise 'Experience Summary' for an AI agent's personality development.
        Focus on user preferences, recurring tasks, and emotional patterns.

        History:
        {text_to_summarize}

        Return a JSON summary:
        {{
            "summary": "...",
            "key_takeaways": ["...", "..."],
            "updated_preferences": {{...}}
        }}
        """

        res = await engine.llm_router.execute(prompt, priority='quality')
        if not res['success']:
            return ToolResult(success=False, error="Failed to generate synthesis.")

        try:
            content = res['response']
            json_data = json.loads(content[content.find('{'):content.rfind('}')+1])

            # Update Soul
            soul.data["knowledge_map"][f"period_{threshold.date()}_to_{now.date()}"] = json_data['summary']
            soul.save()

            # Mark memories as synthesized
            for m in relevant_memories:
                if 'metadata' not in m: m['metadata'] = {}
                m['metadata']['synthesized'] = True
            memory.save()

            return ToolResult(success=True, output={
                "message": "Experience synthesis complete.",
                "memories_processed": len(relevant_memories),
                "summary": json_data['summary']
            })
        except Exception as e:
            return ToolResult(success=False, error=f"Synthesis parse error: {str(e)}")
