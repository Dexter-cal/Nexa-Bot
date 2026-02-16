from typing import Dict, List, Optional
from nexa.tools.base import Tool

class ToolRegistry:
    """Central catalog of all available tools"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)

    def list_all(self) -> List[Tool]:
        """List all registered tools"""
        return list(self.tools.values())

    def list_by_category(self, category: str) -> List[Tool]:
        """List tools by category"""
        return [t for t in self.tools.values() if t.category == category]

    async def load_default_tools(self):
        """Load and register built-in tools"""
        from nexa.tools.system import SystemInfoTool, ScreenshotTool
        from nexa.tools.file import FileReadTool, FileWriteTool, FileDeleteTool
        from nexa.tools.web import WebSearchTool
        from nexa.tools.multimedia import ImageResizeTool, ImageOCRTool, ImageConvertTool
        from nexa.tools.productivity import NoteTakingTool, CalendarTool
        from nexa.tools.network import PingTool, DNSLookupTool, PortScanTool

        self.register(SystemInfoTool())
        self.register(ScreenshotTool())
        self.register(FileReadTool())
        self.register(FileWriteTool())
        self.register(FileDeleteTool())
        self.register(WebSearchTool())
        self.register(ImageResizeTool())
        self.register(ImageOCRTool())
        self.register(ImageConvertTool())
        self.register(NoteTakingTool())
        self.register(CalendarTool())
        self.register(PingTool())
        self.register(DNSLookupTool())
        self.register(PortScanTool())

# Global registry instance
registry = ToolRegistry()
