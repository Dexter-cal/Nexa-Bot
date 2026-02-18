import logging
from nexa.tools.base import Tool, ToolResult
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
import io

logger = logging.getLogger(__name__)

class GenerateMockupsTool(Tool):
    name = "system.generate_mockups"
    description = "Generate visual ASCII/Rich mockups of Nexa's GUI, TUI, and CLI."
    category = "system"
    risk_level = "low"
    parameters = {
        "interface": {"type": "string", "required": True, "description": "gui, tui, or cli"}
    }

    async def execute(self, interface: str, **kwargs) -> ToolResult:
        console = Console(file=io.StringIO(), force_terminal=True, width=80)

        if interface.lower() == "cli":
            console.print(Text(r"""
 ⚡ NEXA BOT - NEURAL ORCHESTRATION ENGINE ⚡
            """, style="bold cyan"))
            console.print(Panel("[bold sky_blue1]Neural Chat Interface Initialized[/]\n[italic text_slate_500]BILL BOT is ready. Type 'exit' to end session.[/]", border_style="sky_blue1"))
            console.print("\n[bold sky_blue1]Max > [/] hi Bill, check my system health")
            console.print("\n[bold sky_blue1]Bill >[/]")
            console.print(Panel("System Health: [green]Optimal[/]\nCPU: 12% | RAM: 4.2GB/16GB", title="Health Check"))

        elif interface.lower() == "tui":
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body")
            )
            layout["body"].split_row(
                Layout(name="sidebar", size=20),
                Layout(name="main")
            )

            layout["header"].update(Panel("[bold cyan]NEXA BOT TUI SETUP v2.0[/]", border_style="blue"))

            table = Table(title="Detected API Keys", box=None)
            table.add_column("Provider", style="cyan")
            table.add_column("Status", style="green")
            table.add_row("OpenAI", "✓ Found")
            table.add_row("Google", "✓ Found")
            table.add_row("Anthropic", "✗ Missing")

            layout["sidebar"].update(Panel(table, border_style="white"))
            layout["main"].update(Panel("Select a provider to configure using arrow keys.\n\n[reverse] > OpenAI [/]\n   Google AI Studio\n   Groq\n   Local (Ollama)", title="Configuration"))

            console.print(layout)

        elif interface.lower() == "gui":
            console.print(Panel("[bold purple]NEXA WEB DASHBOARD (FastAPI + React Mockup)[/]", border_style="purple"))
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Agent ID")
            table.add_column("Role")
            table.add_column("Status")
            table.add_row("agent_a1", "Researcher", "[green]Running")
            table.add_row("agent_b2", "Developer", "[yellow]Paused")

            console.print(table)
            console.print("\n[bold blue]Recent Activity:[/]")
            console.print(" - [dim]10:45 AM[/] Blockchain entry created for 'system.info'")
            console.print(" - [dim]10:46 AM[/] Neural Sync correlated login from Uganda")

        output = console.file.getvalue()
        return ToolResult(success=True, output=output)
