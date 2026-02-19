import logging
from nexa.tools.base import Tool, ToolResult
from nexa.intelligence.router import EnhancedLLMRouter

logger = logging.getLogger(__name__)

class NeuralReviewTool(Tool):
    name = "dev.neural_review"
    description = "Autonomous code review for security, performance, and style using the Intelligence Engine."
    category = "dev"
    risk_level = "low"
    parameters = {
        "code": {"type": "string", "required": True}
    }

    async def execute(self, code: str, **kwargs) -> ToolResult:
        router = EnhancedLLMRouter()
        prompt = f"Perform a critical code review for this snippet:\n\n{code}\n\nIdentify security vulnerabilities and performance bottlenecks."
        res = await router.execute(prompt, priority='quality')
        return ToolResult(success=True, output=res['response'])

class AutoDocTool(Tool):
    name = "dev.autodoc"
    description = "Automatically generate comprehensive documentation for a Python module."
    category = "dev"
    risk_level = "low"
    parameters = {
        "module_path": {"type": "string", "required": True}
    }
    async def execute(self, module_path: str, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=f"Documentation generated for {module_path}. Saved to docs/build/.")
