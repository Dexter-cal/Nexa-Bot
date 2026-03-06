from epex.tools.base import Tool, ToolResult
from typing import Optional, Dict, Any, List

class StoryWriterTool(Tool):
    name = "creative.write_story"
    description = "Write a creative story based on a prompt"
    category = "creative"
    risk_level = "low"
    parameters = {
        "prompt": {"type": "string", "required": True},
        "genre": {"type": "string", "required": False, "default": "science fiction"}
    }

    async def execute(self, prompt: str, genre: str = "science fiction", **kwargs) -> ToolResult:
        # In a real scenario, this would use a specialized model or specific prompt engineering
        return ToolResult(success=True, output=f"Generated a {genre} story about: {prompt}")

class ImageGenTool(Tool):
    name = "creative.generate_image"
    description = "Generate an image from a text prompt"
    category = "creative"
    risk_level = "low"
    parameters = {
        "prompt": {"type": "string", "required": True}
    }

    async def execute(self, prompt: str, **kwargs) -> ToolResult:
        # Mocking image generation
        return ToolResult(success=True, output=f"Image generated for: {prompt}")
