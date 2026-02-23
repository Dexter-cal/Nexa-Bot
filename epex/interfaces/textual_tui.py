import asyncio
import psutil
import logging
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, Button, ListItem, ListView, Label, ProgressBar, TabbedContent, TabPane
from textual.reactive import reactive
from textual.screen import Screen
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.console import RenderableType

from epex.core.engine import engine
from epex.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class SystemStatusWidget(Static):
    """Widget to display real-time system status."""
    cpu_usage = reactive(0.0)
    ram_usage = reactive(0.0)
    disk_free = reactive(0.0)

    def on_mount(self) -> None:
        self.set_interval(1.0, self.update_stats)

    def update_stats(self) -> None:
        self.cpu_usage = psutil.cpu_percent()
        self.ram_usage = psutil.virtual_memory().percent
        self.disk_free = psutil.disk_usage('/').free / (1024**3)

    def render(self) -> RenderableType:
        table = Table.grid(padding=(0, 1))
        table.add_column("Stat", style="bold cyan")
        table.add_column("Value")

        table.add_row("CPU", f"{self.cpu_usage}%")
        table.add_row("RAM", f"{self.ram_usage}%")
        table.add_row("Disk", f"{self.disk_free:.1f} GB")

        return Panel(table, title="📊 SYSTEM", border_style="blue")

class ChatMessage(Static):
    """A widget for chat messages."""
    def __init__(self, sender: str, message: str, color: str = "white"):
        super().__init__()
        self.sender = sender
        self.message = message
        self.color = color

    def render(self) -> str:
        return f"[bold {self.color}]{self.sender}:[/] {self.message}"

class ChatPanel(Vertical):
    """The main chat interaction panel."""
    def compose(self) -> ComposeResult:
        yield Vertical(id="chat-history")
        yield Input(placeholder="nexa ❯ Type message...", id="chat-input")

    async def on_mount(self) -> None:
        history = self.query_one("#chat-history")
        history.mount(ChatMessage("Nexa", "Welcome back! I'm ready to assist.", "green"))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if not event.value:
            return

        history = self.query_one("#chat-history")
        history.mount(ChatMessage("You", event.value, "cyan"))
        event.input.value = ""
        history.scroll_end()

        # Call engine
        response_data = await engine.execute_command(event.value)
        response = response_data.get('response', "Error: No response")
        model = response_data.get('model', 'unknown')

        history.mount(ChatMessage(f"Nexa ({model})", response, "green"))
        history.scroll_end()

class AgentItem(ListItem):
    """Widget for an individual agent in the list."""
    def __init__(self, agent_id: str, role: str, status: str, progress: float):
        super().__init__()
        self.agent_id = agent_id
        self.role = role
        self.status = status
        self.progress = progress

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(f"{self.agent_id}", variant="id"),
            Label(f"{self.role}", variant="role"),
            Label(f"{self.status}", variant="status"),
            ProgressBar(total=100, show_percentage=True, id=f"pb-{self.agent_id}"),
            classes="agent-row"
        )

    def on_mount(self) -> None:
        self.query_one(ProgressBar).update(progress=self.progress)

class AgentManagerView(Vertical):
    """View for managing agents."""
    def compose(self) -> ComposeResult:
        yield Label("🤖 ACTIVE AGENTS (3/10)", classes="panel-header")
        yield ListView(
            AgentItem("agent_3a2f", "developer", "RUNNING", 78),
            AgentItem("agent_7b1c", "researcher", "RUNNING", 45),
            AgentItem("agent_9d4e", "hacker", "DONE", 100),
            id="agent-list"
        )
        yield Horizontal(
            Button("Spawn New", variant="success"),
            Button("Kill All", variant="error"),
            classes="action-buttons"
        )

class PrivacyGuardianView(Vertical):
    """View for privacy monitoring."""
    def compose(self) -> ComposeResult:
        yield Label("🛡️ PRIVACY GUARDIAN", classes="panel-header")
        yield Vertical(
            Static(Panel("[red]✗ Email found in CompanyXYZ breach[/]\n[dim]user@example.com[/]\nExposed: email, password hash, name", title="🚨 CRITICAL", border_style="red")),
            Static(Panel("[yellow]⚠ API key in old backup[/]\n[dim]Downloads/old_project.zip[/]\nType: OpenAI API", title="⚠ WARNING", border_style="yellow")),
            id="privacy-alerts"
        )
        yield Label("MONITORING: 📧 3 emails  •  🔑 12 keys  •  🔐 47 passwords", id="privacy-stats")

class KeyManagerView(Vertical):
    """View for managing API keys."""
    def compose(self) -> ComposeResult:
        yield Label("🔑 API KEYS MANAGER", classes="panel-header")
        yield ListView(id="key-list-view")
        yield Horizontal(
            Button("Add New Key", variant="primary"),
            Button("Test All", variant="default"),
            classes="action-buttons"
        )

    async def on_mount(self) -> None:
        self.set_interval(5.0, self.refresh_keys)
        await self.refresh_keys()

    async def refresh_keys(self) -> None:
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        manager = UniversalAPIKeyManager()
        status = await manager.get_connected_providers()

        list_view = self.query_one("#key-list-view")
        list_view.clear()

        for p, online in status.items():
            symbol = "●" if online else "○"
            color = "green" if online else "red"
            list_view.append(ListItem(Label(f"[{color}]{symbol}[/] {p.capitalize():15} | {'Online' if online else 'Offline'}")))

class EpexTextualApp(App):
    """The main Textual TUI Application for EPEX."""

    CSS = """
    Screen {
        background: #0a0e1a;
    }

    #main-container {
        height: 100%;
    }

    #side-panel {
        width: 25%;
        border-right: solid #111827;
        background: #111827;
    }

    #center-panel {
        width: 50%;
    }

    #right-panel {
        width: 25%;
        border-left: solid #111827;
        background: #111827;
    }

    .screen-title {
        text-align: center;
        width: 100%;
        background: $accent;
        color: $text;
        padding: 1;
        margin-bottom: 1;
        bold: True;
    }

    #chat-history {
        height: 1fr;
        overflow-y: scroll;
        padding: 1;
    }

    #chat-input {
        margin: 1;
        border: solid #00e5ff;
    }

    .agent-row {
        height: 3;
        align: middle;
        padding: 0 1;
    }

    .agent-row Label {
        width: 1fr;
    }

    .action-buttons {
        height: 3;
        align: center middle;
        margin-top: 1;
    }

    ListItem {
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("f1", "switch_tab('chat')", "Chat"),
        Binding("f2", "switch_tab('agents')", "Agents"),
        Binding("f3", "switch_tab('privacy')", "Privacy"),
        Binding("f4", "switch_tab('keys')", "Keys"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Horizontal(
            Vertical(
                Label(" NAVIGATION", id="nav-header"),
                ListView(
                    ListItem(Label("💬 Chat"), id="nav-chat"),
                    ListItem(Label("🤖 Agents"), id="nav-agents"),
                    ListItem(Label("🛡️ Privacy"), id="nav-privacy"),
                    ListItem(Label("🔑 Keys"), id="nav-keys"),
                    ListItem(Label("⚙️ Settings"), id="nav-settings"),
                ),
                Label(" PROVIDERS", id="prov-header"),
                ListView(id="provider-list"),
                id="side-panel"
            ),
            Vertical(
                TabbedContent(
                    TabPane("Chat", ChatPanel(), id="chat-pane"),
                    TabPane("Agents", AgentManagerView(), id="agents-pane"),
                    TabPane("Privacy", PrivacyGuardianView(), id="privacy-pane"),
                    TabPane("Keys", KeyManagerView(), id="keys-pane"),
                    id="main-tabs"
                ),
                id="center-panel"
            ),
            Vertical(
                SystemStatusWidget(),
                Static(Panel("No recent alerts", title="🔔 ALERTS", border_style="yellow")),
                id="right-panel"
            ),
            id="main-container"
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.title = "NEXA APEX • Command Center"
        # Start engine
        asyncio.create_task(engine.start())
        await self.update_providers()

    async def update_providers(self) -> None:
        status_map = await engine.llm_router.api_manager.get_connected_providers()
        prov_list = self.query_one("#provider-list")
        prov_list.clear()
        for p, online in status_map.items():
            symbol = "●" if online else "○"
            color = "green" if online else "grey50"
            prov_list.append(ListItem(Label(f"[{color}]{symbol}[/] {p.capitalize()}")))

    def action_switch_tab(self, tab: str) -> None:
        self.query_one(TabbedContent).active = f"{tab}-pane"

if __name__ == "__main__":
    app = EpexTextualApp()
    app.run()
