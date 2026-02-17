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

    def register_from_code(self, code: str):
        """Register a tool from its Python source code"""
        import tempfile
        import importlib.util
        import os
        import uuid
        import sys

        module_name = f"dynamic_tool_{uuid.uuid4().hex}"
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as f:
                f.write(code)
                temp_path = f.name

            spec = importlib.util.spec_from_file_location(module_name, temp_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr in dir(module):
                val = getattr(module, attr)
                if isinstance(val, type) and issubclass(val, Tool) and val is not Tool:
                    tool_instance = val()
                    self.register(tool_instance)
                    return tool_instance
            raise ValueError("No Tool class found in code")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    async def load_default_tools(self):
        """Load and register built-in tools"""
        from nexa.tools.system import SystemInfoTool, ScreenshotTool, MouseControlTool, KeyboardControlTool, ProcessListTool, NetworkStatsTool, TerminalTool
        from nexa.tools.file import FileReadTool, FileWriteTool, FileDeleteTool
        from nexa.tools.web import WebSearchTool, WebScrapeTool, WebScreenshotTool, WebWhoisTool, WebHttpRequestTool
        from nexa.tools.multimedia import ImageResizeTool, ImageOCRTool, ImageConvertTool
        from nexa.tools.productivity import NoteTakingTool, CalendarTool
        from nexa.tools.network import PingTool, DNSLookupTool, PortScanTool
        from nexa.tools.meta import ToolGeneratorTool, ToolTesterTool, SelfUpdaterTool, MirrorWorldSimulateTool
        from nexa.tools.security import VulnerabilityScannerTool
        from nexa.tools.learning import ResearchTopicTool, FindAcademicPapersTool
        from nexa.tools.creative import StoryWriterTool, ImageGenTool
        from nexa.tools.social import TwitterPostTool, HashtagGeneratorTool, MonitorMentionsTool
        from nexa.tools.finance import StockPriceTool, CryptoPriceTool
        from nexa.tools.pdf import PDFMergeTool, PDFSplitTool
        from nexa.tools.maint import CleanTempFilesTool, DiskHealthTool
        from nexa.tools.voice import TextToSpeechTool, SpeechToTextTool
        from nexa.tools.communication import TelegramSendTool, EmailSendTool, AlertPushTool, GmailSearchTool, WhatsAppSendTool

        self.register(SystemInfoTool())
        self.register(ScreenshotTool())
        self.register(MouseControlTool())
        self.register(KeyboardControlTool())
        self.register(ProcessListTool())
        self.register(NetworkStatsTool())
        self.register(TerminalTool())
        self.register(FileReadTool())
        self.register(FileWriteTool())
        self.register(FileDeleteTool())
        self.register(WebSearchTool())
        self.register(WebScrapeTool())
        self.register(WebScreenshotTool())
        self.register(WebWhoisTool())
        self.register(WebHttpRequestTool())
        self.register(ImageResizeTool())
        self.register(ImageOCRTool())
        self.register(ImageConvertTool())
        self.register(NoteTakingTool())
        self.register(CalendarTool())
        self.register(PingTool())
        self.register(DNSLookupTool())
        self.register(PortScanTool())
        self.register(ToolGeneratorTool())
        self.register(VulnerabilityScannerTool())
        self.register(ResearchTopicTool())
        self.register(FindAcademicPapersTool())
        self.register(StoryWriterTool())
        self.register(ImageGenTool())
        self.register(TwitterPostTool())
        self.register(HashtagGeneratorTool())
        self.register(MonitorMentionsTool())
        self.register(StockPriceTool())
        self.register(CryptoPriceTool())
        self.register(PDFMergeTool())
        self.register(PDFSplitTool())
        self.register(CleanTempFilesTool())
        self.register(DiskHealthTool())
        self.register(TextToSpeechTool())
        self.register(SpeechToTextTool())
        self.register(TelegramSendTool())
        self.register(EmailSendTool())
        self.register(AlertPushTool())
        self.register(GmailSearchTool())
        self.register(WhatsAppSendTool())
        self.register(ToolTesterTool())
        self.register(SelfUpdaterTool())
        self.register(MirrorWorldSimulateTool())

# Global registry instance
registry = ToolRegistry()
