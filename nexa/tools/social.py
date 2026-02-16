from nexa.tools.base import Tool, ToolResult
from typing import Optional, Dict, Any, List

class TwitterPostTool(Tool):
    name = "social.twitter_post"
    description = "Post a message to Twitter/X"
    category = "social"
    risk_level = "medium"
    parameters = {
        "message": {"type": "string", "required": True}
    }

    async def execute(self, message: str, **kwargs) -> ToolResult:
        # Mocking social media post
        return ToolResult(success=True, output=f"Successfully posted to Twitter/X: {message}")

class HashtagGeneratorTool(Tool):
    name = "social.generate_hashtags"
    description = "Generate relevant hashtags for a topic"
    category = "social"
    risk_level = "low"
    parameters = {
        "topic": {"type": "string", "required": True}
    }

    async def execute(self, topic: str, **kwargs) -> ToolResult:
        # Simple hashtag generator
        hashtags = [f"#{word.strip()}" for word in topic.split()]
        return ToolResult(success=True, output=hashtags)

class MonitorMentionsTool(Tool):
    name = "social.monitor_mentions"
    description = "Monitor social media for mentions of a specific keyword or brand"
    category = "social"
    risk_level = "low"
    parameters = {
        "keyword": {"type": "string", "required": True},
        "platforms": {"type": "list", "required": False, "default": ["twitter"]}
    }

    async def execute(self, keyword: str, platforms: List[str] = ["twitter"], **kwargs) -> ToolResult:
        # Mocking mention monitoring
        mentions = [
            {"platform": "twitter", "user": "@ai_enthusiast", "text": f"Just tried #NexaBot! It's awesome. Mentioned: {keyword}"}
        ]
        return ToolResult(success=True, output=mentions)
