from typing import Dict, List, Optional
from epex.tools.base import Tool

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
        from epex.tools.system import SystemInfoTool, ScreenshotTool, MouseControlTool, KeyboardControlTool, ProcessListTool, NetworkStatsTool, TerminalTool, VisionAnalyzeTool, SelectCaptureTool, ServiceManagerTool, RegistryExpertTool
        from epex.tools.file import FileReadTool, FileWriteTool, FileDeleteTool
        from epex.tools.web import WebSearchTool, WebScrapeTool, WebScreenshotTool, WebWhoisTool, WebHttpRequestTool
        from epex.tools.multimedia import ImageResizeTool, ImageOCRTool, ImageConvertTool
        from epex.tools.productivity import NoteTakingTool, CalendarTool
        from epex.tools.network import PingTool, DNSLookupTool, PortScanTool
        from epex.tools.meta import ToolGeneratorTool, ApexToolBuilderTool, ToolTesterTool, SelfUpdaterTool, MirrorWorldSimulateTool, ShareToolWithPeerTool, RequestToolFromPeerTool, ScenarioTemplateTool, NeuralBridgeSyncTool
        from epex.tools.dream import DreamSimulationTool
        from epex.tools.security import VulnerabilityScannerTool, DataLockdownTool
        from epex.tools.anonymity import StealthModeTool, MetadataScrubberTool
        from epex.tools.defense import HoneyPotTool, SystemIntegrityMonitorTool
        from epex.tools.intuition import SelfSecurityAuditTool as SelfAISecurityAuditTool, IntentPredictionTool
        from epex.tools.security_audit import SelfSecurityAuditTool
        from epex.tools.learning import ResearchTopicTool, FindAcademicPapersTool
        from epex.tools.creative import StoryWriterTool, ImageGenTool
        from epex.tools.social import TwitterPostTool, HashtagGeneratorTool, MonitorMentionsTool, DiscordWebhookTool, TelegramBotManagerTool, WhatsAppGatewayTool
        from epex.tools.finance import StockPriceTool, CryptoPriceTool
        from epex.tools.pdf import PDFMergeTool, PDFSplitTool
        from epex.tools.maint import DiskHealthTool, FileRecoveryTool, SystemOptimizerTool, RegistryRepairTool, DiskUsageAnalyzerTool, BootRepairTool, DriverManagerTool, DeepScrubTool, PredictiveMaintenanceTool
        from epex.tools.auto_repair import AutoRepairWizardTool
        from epex.tools.voice import TextToSpeechTool, SpeechToTextTool
        from epex.tools.communication import TelegramSendTool, EmailSendTool, AlertPushTool, GmailSearchTool, WhatsAppSendTool
        from epex.tools.hardware import AndroidControlTool, GPIOControlTool, BluetoothManagerTool, WiFiManagerTool
        from epex.tools.forensics import ForensicOSINTTool
        from epex.tools.forensics_v2 import BreachCheckTool, MalwarePersistenceScannerTool
        from epex.tools.dev_tools import NeuralReviewTool, AutoDocTool
        from epex.tools.spatial import SpatialIntelligenceTool
        from epex.tools.automation_finance import SignUpAutomationTool, BudgetManagerTool, AccountSyncTool
        from epex.tools.automation import InternetInteractorTool, AccountCreatorTool
        from epex.tools.omni_search import OmniSearchTool
        from epex.tools.visualizer import GenerateMockupsTool
        from epex.tools.monitoring import SignalMonitorTool
        from epex.tools.memory_ops import MemoryIndexingTool, MemorySearchTool
        from epex.tools.network_ops import TunnelManagerTool, PeerDiscoveryTool
        from epex.tools.final_legendary import SystemAuditTool, SecurityHardeningTool, DeepOSINTTool
        from epex.tools.model_zoo import ModelZooExplorerTool
        from epex.tools.pairing import GeneratePairingQRTool
        from epex.tools.evolution import SelfEvolutionTool, LogicRefactorTool
        from epex.tools.security import FirewallOverrideTool
        from epex.tools.advanced_hardware import BiometricAuthTool, NeuralPulseTool, IoTControlTool
        from epex.tools.ethereal_sync import EtherealSyncTool
        from epex.tools.chronos import ChronosBranchTool
        from epex.tools.neural_graph import NeuralGraphTool
        from epex.tools.stego import SteganographyTool
        from epex.tools.plugins import PluginLoaderTool
        from epex.tools.swarm_evolution import EvolveSwarmTool
        from epex.tools.soundscape import NeuralSoundscapeTool
        from epex.tools.legendary_ext import LinodeDeployTool, HuggingFaceHubTool
        from epex.tools.legendary_forensics import SocialMediaLookupTool, DomainIntelligenceTool, DeepFileRecoveryTool, MemoryDumpAnalysisTool
        from epex.tools.document import DocumentParseTool, VisionAnalyzeAttachmentTool
        from epex.tools.intelligence import NeuroLinkTool
        from epex.intelligence.council import CouncilCalibrateTool
        from epex.tools.snapshot import QuantumSnapshotTool, QuantumRestoreTool
        from epex.intelligence.macros import MacroSuggesterTool, MacroRegisterTool
        from epex.memory.synthesis import MemorySynthesisTool
        from epex.tools.reset import SystemResetTool

        self.register(SystemInfoTool())
        self.register(ScreenshotTool())
        self.register(MouseControlTool())
        self.register(KeyboardControlTool())
        self.register(ProcessListTool())
        self.register(NetworkStatsTool())
        self.register(TerminalTool())
        self.register(VisionAnalyzeTool())
        self.register(SelectCaptureTool())
        self.register(ServiceManagerTool())
        self.register(RegistryExpertTool())
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
        self.register(ApexToolBuilderTool())
        self.register(VulnerabilityScannerTool())
        self.register(DataLockdownTool())
        self.register(StealthModeTool())
        self.register(MetadataScrubberTool())
        self.register(HoneyPotTool())
        self.register(SystemIntegrityMonitorTool())
        self.register(SelfAISecurityAuditTool())
        self.register(IntentPredictionTool())
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
        self.register(NeuralPulseTool())
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
        self.register(NeuroLinkTool())
        self.register(CouncilCalibrateTool())
        self.register(QuantumSnapshotTool())
        self.register(QuantumRestoreTool())
        self.register(MacroSuggesterTool())
        self.register(MacroRegisterTool())
        self.register(MemorySynthesisTool())
        self.register(SystemResetTool())
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
