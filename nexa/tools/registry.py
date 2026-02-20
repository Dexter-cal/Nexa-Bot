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
        from nexa.tools.system import SystemInfoTool, ScreenshotTool, MouseControlTool, KeyboardControlTool, ProcessListTool, NetworkStatsTool, TerminalTool, VisionAnalyzeTool
        from nexa.tools.file import FileReadTool, FileWriteTool, FileDeleteTool
        from nexa.tools.web import WebSearchTool, WebScrapeTool, WebScreenshotTool, WebWhoisTool, WebHttpRequestTool
        from nexa.tools.multimedia import ImageResizeTool, ImageOCRTool, ImageConvertTool
        from nexa.tools.productivity import NoteTakingTool, CalendarTool
        from nexa.tools.network import PingTool, DNSLookupTool, PortScanTool
        from nexa.tools.meta import ToolGeneratorTool, ToolTesterTool, SelfUpdaterTool, MirrorWorldSimulateTool, ShareToolWithPeerTool, RequestToolFromPeerTool, ScenarioTemplateTool, NeuralBridgeSyncTool
        from nexa.tools.dream import DreamSimulationTool
        from nexa.tools.security import VulnerabilityScannerTool
        from nexa.tools.security_audit import SelfSecurityAuditTool
        from nexa.tools.learning import ResearchTopicTool, FindAcademicPapersTool
        from nexa.tools.creative import StoryWriterTool, ImageGenTool
        from nexa.tools.social import TwitterPostTool, HashtagGeneratorTool, MonitorMentionsTool, DiscordWebhookTool, TelegramBotManagerTool, WhatsAppGatewayTool
        from nexa.tools.finance import StockPriceTool, CryptoPriceTool
        from nexa.tools.pdf import PDFMergeTool, PDFSplitTool
        from nexa.tools.maint import DiskHealthTool, FileRecoveryTool, SystemOptimizerTool, RegistryRepairTool, DiskUsageAnalyzerTool, BootRepairTool, DriverManagerTool, DeepScrubTool, PredictiveMaintenanceTool
        from nexa.tools.auto_repair import AutoRepairWizardTool
        from nexa.tools.voice import TextToSpeechTool, SpeechToTextTool
        from nexa.tools.communication import TelegramSendTool, EmailSendTool, AlertPushTool, GmailSearchTool, WhatsAppSendTool
        from nexa.tools.hardware import AndroidControlTool, GPIOControlTool, BluetoothManagerTool, WiFiManagerTool
        from nexa.tools.forensics import ForensicOSINTTool
        from nexa.tools.forensics_v2 import BreachCheckTool, MalwarePersistenceScannerTool
        from nexa.tools.dev_tools import NeuralReviewTool, AutoDocTool
        from nexa.tools.spatial import SpatialIntelligenceTool
        from nexa.tools.automation_finance import SignUpAutomationTool, BudgetManagerTool, AccountSyncTool
        from nexa.tools.automation import InternetInteractorTool, AccountCreatorTool
        from nexa.tools.omni_search import OmniSearchTool
        from nexa.tools.visualizer import GenerateMockupsTool
        from nexa.tools.monitoring import SignalMonitorTool
        from nexa.tools.memory_ops import MemoryIndexingTool, MemorySearchTool
        from nexa.tools.network_ops import TunnelManagerTool, PeerDiscoveryTool
        from nexa.tools.final_legendary import SystemAuditTool, SecurityHardeningTool, DeepOSINTTool
        from nexa.tools.model_zoo import ModelZooExplorerTool
        from nexa.tools.pairing import GeneratePairingQRTool
        from nexa.tools.evolution import SelfEvolutionTool, LogicRefactorTool
        from nexa.tools.security import FirewallOverrideTool
        from nexa.tools.advanced_hardware import BiometricAuthTool, IoTControlTool
        from nexa.tools.ethereal_sync import EtherealSyncTool
        from nexa.tools.chronos import ChronosBranchTool
        from nexa.tools.neural_graph import NeuralGraphTool
        from nexa.tools.stego import SteganographyTool
        from nexa.tools.plugins import PluginLoaderTool
        from nexa.tools.swarm_evolution import EvolveSwarmTool
        from nexa.tools.soundscape import NeuralSoundscapeTool
        from nexa.tools.legendary_ext import LinodeDeployTool, HuggingFaceHubTool
        from nexa.tools.legendary_forensics import SocialMediaLookupTool, DomainIntelligenceTool, DeepFileRecoveryTool, MemoryDumpAnalysisTool
        from nexa.tools.document import DocumentParseTool, VisionAnalyzeAttachmentTool

        self.register(SystemInfoTool())
        self.register(ScreenshotTool())
        self.register(MouseControlTool())
        self.register(KeyboardControlTool())
        self.register(ProcessListTool())
        self.register(NetworkStatsTool())
        self.register(TerminalTool())
        self.register(VisionAnalyzeTool())
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
        self.register(SelfSecurityAuditTool())
        self.register(ResearchTopicTool())
        self.register(FindAcademicPapersTool())
        self.register(StoryWriterTool())
        self.register(ImageGenTool())
        self.register(TwitterPostTool())
        self.register(HashtagGeneratorTool())
        self.register(MonitorMentionsTool())
        self.register(DiscordWebhookTool())
        self.register(TelegramBotManagerTool())
        self.register(WhatsAppGatewayTool())
        self.register(StockPriceTool())
        self.register(CryptoPriceTool())
        self.register(PDFMergeTool())
        self.register(PDFSplitTool())
        self.register(FileRecoveryTool())
        self.register(SystemOptimizerTool())
        self.register(RegistryRepairTool())
        self.register(DeepScrubTool())
        self.register(PredictiveMaintenanceTool())
        self.register(AutoRepairWizardTool())
        self.register(SecurityHardeningTool())
        self.register(DiskUsageAnalyzerTool())
        self.register(BootRepairTool())
        self.register(DriverManagerTool())
        self.register(DiskHealthTool())
        self.register(TextToSpeechTool())
        self.register(SpeechToTextTool())
        self.register(TelegramSendTool())
        self.register(EmailSendTool())
        self.register(AlertPushTool())
        self.register(GmailSearchTool())
        self.register(WhatsAppSendTool())
        self.register(AndroidControlTool())
        self.register(GPIOControlTool())
        self.register(BluetoothManagerTool())
        self.register(WiFiManagerTool())
        self.register(ForensicOSINTTool())
        self.register(BreachCheckTool())
        self.register(MalwarePersistenceScannerTool())
        self.register(NeuralReviewTool())
        self.register(AutoDocTool())
        self.register(SpatialIntelligenceTool())
        self.register(SignUpAutomationTool())
        self.register(InternetInteractorTool())
        self.register(OmniSearchTool())
        self.register(DeepOSINTTool())
        self.register(AccountCreatorTool())
        self.register(SignalMonitorTool())
        self.register(MemoryIndexingTool())
        self.register(MemorySearchTool())
        self.register(TunnelManagerTool())
        self.register(PeerDiscoveryTool())
        self.register(GeneratePairingQRTool())
        self.register(SelfEvolutionTool())
        self.register(LogicRefactorTool())
        self.register(FirewallOverrideTool())
        self.register(BiometricAuthTool())
        self.register(IoTControlTool())
        self.register(EtherealSyncTool())
        self.register(ChronosBranchTool())
        self.register(NeuralGraphTool())
        self.register(SystemAuditTool())
        self.register(ModelZooExplorerTool())
        self.register(SteganographyTool())
        self.register(PluginLoaderTool())
        self.register(EvolveSwarmTool())
        self.register(NeuralSoundscapeTool())
        self.register(LinodeDeployTool())
        self.register(HuggingFaceHubTool())
        self.register(SocialMediaLookupTool())
        self.register(DomainIntelligenceTool())
        self.register(DeepFileRecoveryTool())
        self.register(MemoryDumpAnalysisTool())
        self.register(DocumentParseTool())
        self.register(VisionAnalyzeAttachmentTool())
        self.register(GenerateMockupsTool())
        self.register(BudgetManagerTool())
        self.register(AccountSyncTool())
        self.register(ToolTesterTool())
        self.register(SelfUpdaterTool())
        self.register(ShareToolWithPeerTool())
        self.register(RequestToolFromPeerTool())
        self.register(MirrorWorldSimulateTool())
        self.register(ScenarioTemplateTool())
        self.register(NeuralBridgeSyncTool())
        self.register(DreamSimulationTool())

# Global registry instance
registry = ToolRegistry()
