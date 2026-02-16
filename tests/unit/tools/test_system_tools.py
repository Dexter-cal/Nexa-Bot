import pytest
from nexa.tools.system import SystemInfoTool

class TestSystemInfoTool:
    """Test suite for SystemInfoTool"""

    @pytest.fixture
    def tool(self):
        return SystemInfoTool()

    def test_tool_properties(self, tool):
        """Test tool has correct properties"""
        assert tool.name == "system.info"
        assert tool.category == "system"
        assert tool.risk_level == "low"

    @pytest.mark.asyncio
    async def test_execute_success(self, tool):
        """Test successful execution"""
        result = await tool.execute()

        assert result.success is True
        assert "cpu" in result.output
        assert "memory" in result.output
        assert "disk" in result.output
