import logging
from nexa.tools.base import Tool, ToolResult
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
import io

logger = logging.getLogger(__name__)

class GenerateMockupsTool(Tool):
    name = "system.generate_mockups"
    description = "Generate visual ASCII/Rich mockups of Nexa's GUI, TUI, and CLI."
    category = "system"
    risk_level = "low"
    parameters = {
        "interface": {"type": "string", "required": False, "description": "gui, tui, or cli"}
    }

    async def execute(self, interface: str = None, **kwargs) -> ToolResult:
        console = Console(file=io.StringIO(), force_terminal=True, width=100)

        if not interface or interface.lower() == "cli":
            console.print(Text(r"""
 ⚡ NEXA BOT - NEURAL ORCHESTRATION ENGINE ⚡
            """, style="bold cyan"))
            console.print(Panel("[bold sky_blue1]Neural Chat Interface Initialized[/]\n[italic text_slate_500]BILL BOT is ready. Type 'exit' to end session.[/]", border_style="sky_blue1", title="CLI v2.0"))
            console.print("\n[bold sky_blue1]Max > [/] hi Bill, check my system health")
            console.print("\n[bold sky_blue1]Bill >[/]")
            table = Table(title="System Health: [green]Optimal[/]", box=None)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="bold white")
            table.add_row("CPU Usage", "12% [green]|||[/]         ")
            table.add_row("RAM Usage", "4.2GB/16GB [green]||||[/]       ")
            console.print(Panel(table, border_style="green"))

        if not interface or interface.lower() == "tui":
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body")
            )
            layout["body"].split_row(
                Layout(name="sidebar", size=30),
                Layout(name="main")
            )

            layout["header"].update(Panel("[bold cyan]NEXA BOT TUI SETUP v2.0[/]", border_style="blue"))

            table = Table(title="Detected API Keys", box=None)
            table.add_column("Provider", style="cyan")
            table.add_column("Status", style="green")
            table.add_row("OpenAI", "✓ Found")
            table.add_row("Google", "✓ Found")
            table.add_row("Anthropic", "✗ Missing")

            layout["sidebar"].update(Panel(table, border_style="white", title="Inventory"))
            layout["main"].update(Panel("Select a provider to configure using arrow keys.\n\n[reverse white on blue] > OpenAI [/]\n   Google AI Studio\n   Groq\n   Local (Ollama)\n   HuggingFace", title="Configuration"))

            console.print("\n" + "="*100 + "\n")
            console.print(layout)

        if not interface or interface.lower() == "gui":
            console.print("\n" + "="*100 + "\n")
            console.print(Panel("[bold purple]NEXA WEB DASHBOARD (FastAPI + React Mockup)[/]", border_style="purple", title="GUI v2.0"))

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Agent ID")
            table.add_column("Role")
            table.add_column("Status")
            table.add_column("Health")
            table.add_row("agent_a1", "Researcher", "[green]Running", "[green]Healthy")
            table.add_row("agent_b2", "Developer", "[yellow]Paused", "[green]Healthy")
            table.add_row("agent_c3", "Hacker", "[red]Disconnected", "[red]Critical")

            console.print(table)

            p1 = Panel("Neural Sync Status: [green]Active[/]\nNodes Connected: 5\nLast Sync: 1 min ago", title="Neural Sync", border_style="cyan")
            p2 = Panel("Blockchain Audit: [green]Immutable[/]\nTotal Entries: 1,245\nLatest: system.info", title="Audit Trail", border_style="blue")
            console.print(Columns([p1, p2]))

        output = console.file.getvalue()
        return ToolResult(success=True, output=output)
