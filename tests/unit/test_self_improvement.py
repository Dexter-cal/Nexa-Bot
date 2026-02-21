import pytest
import os
from epex.tools.meta import ToolGeneratorTool, ToolTesterTool, SelfUpdaterTool
from epex.tools.registry import registry

class TestSelfImprovement:
    @pytest.mark.asyncio
    async def test_tool_generation(self):
        from unittest.mock import AsyncMock
        mock_router = AsyncMock()
        mock_router.execute.return_value = {
            "success": True,
            "response": "```python\nclass MyTool(Tool):\n    pass\n```"
        }

        tool = ToolGeneratorTool(llm_router=mock_router)
        spec = {
            "name": "custom.test_tool",
            "description": "A tool that returns a test string",
            "parameters": {"test_input": {"type": "string", "required": True}}
        }

        result = await tool.execute(spec=spec)
        assert result.success is True
        assert "class MyTool(Tool):" in result.output

    @pytest.mark.asyncio
    async def test_tool_testing_and_registration(self):
        code = """
from epex.tools.base import Tool, ToolResult

class DynamicHelloWorldTool(Tool):
    name = "custom.dynamic_hello"
    description = "Says hello"
    category = "custom"
    risk_level = "low"
    parameters = {"name": {"type": "string", "required": True}}

    async def execute(self, name: str, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=f"Dynamic Hello, {name}!")
"""
        # Test the code
        tester = ToolTesterTool()
        test_cases = [{"name": "Jules"}]
        test_result = await tester.execute(code=code, test_cases=test_cases)
        assert test_result.success is True
        assert test_result.output[0]['success'] is True
        assert test_result.output[0]['output'] == "Dynamic Hello, Jules!"

        # Register the code
        dyn_tool = registry.register_from_code(code)
        assert dyn_tool.name == "custom.dynamic_hello"
        assert registry.get("custom.dynamic_hello") is not None

        # Execute registered tool
        exec_result = await registry.get("custom.dynamic_hello").execute(name="World")
        assert exec_result.output == "Dynamic Hello, World!"

    @pytest.mark.asyncio
    async def test_self_update(self):
        # Create a dummy component
        dummy_file = "epex/dummy_component.py"
        with open(dummy_file, 'w') as f:
            f.write("def hello(): return 'old'")

        updater = SelfUpdaterTool()
        new_code = "def hello(): return 'new'"
        result = await updater.execute(component_path=dummy_file, new_code=new_code)

        assert result.success is True
        with open(dummy_file, 'r') as f:
            content = f.read()
        assert content == new_code
        assert os.path.exists(f"{dummy_file}.bak")

        # Cleanup
        os.remove(dummy_file)
        os.remove(f"{dummy_file}.bak")
