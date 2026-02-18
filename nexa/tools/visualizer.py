import logging
from nexa.tools.base import Tool, ToolResult
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
import io

logger = logging.getLogger(__name__)

BANNER_ASCII = r"""
███╗   ██╗███████╗██╗  ██╗ █████╗     ██████╗  ██████╗ ████████╗
████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗    ██╔══██╗██╔═══██╗╚══██╔══╝
██╔██╗ ██║█████╗   ╚███╔╝ ███████║    ██████╔╝██║   ██║   ██║
██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║    ██╔══██╗██║   ██║   ██║
██║ ╚████║███████╗██╔╝ ██╗██║  ██║    ██████╔╝╚██████╔╝   ██║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝
             NEURAL ORCHESTRATION ENGINE v2.5
"""

class GenerateMockupsTool(Tool):
    name = "system.generate_mockups"
    description = "Generate visual ASCII/Rich mockups of Nexa's GUI, TUI, and CLI."
    category = "system"
    risk_level = "low"
    parameters = {
        "interface": {"type": "string", "required": False, "description": "gui, tui, or cli"}
    }

    async def execute(self, interface: str = None, **kwargs) -> ToolResult:
        console = Console(file=io.StringIO(), force_terminal=True, width=120)

        if not interface or interface.lower() == "cli":
            console.print(Align.center(Text(BANNER_ASCII, style="bold cyan")))
            console.print(Panel(Align.center("[bold sky_blue1]Neural Chat Interface Initialized[/]\n[italic text_slate_500]BILL BOT (Aura: Witty | Mood: Efficient) is ready.[/]"), border_style="sky_blue1", title="CLI v2.5"))

            console.print("\n[bold sky_blue1]Max > [/] Bill, analyze the steganographic data in 'secret.png' and spawn a researcher agent to look for correlations.")
            console.print("\n[bold sky_blue1]Bill >[/]")

            with console.status("[bold green]Synthesizing Strategy..."):
                tree = Table.grid(padding=1)
                tree.add_column(style="dim")
                tree.add_column()
                tree.add_row(" ├─", "Decoding steganography in 'secret.png'...")
                tree.add_row(" ├─", "[green]✓[/] Message found: 'PROJECT_X_2025'")
                tree.add_row(" ├─", "Spawning Researcher Agent (agent_44)...")
                tree.add_row(" └─", "[green]✓[/] agent_44 searching deep-web archives...")

            console.print(Panel(tree, border_style="green", title="Thought Chain"))
            console.print("\n[bold sky_blue1]Bill >[/] Done! I've decoded the image and agent_44 is currently cross-referencing the results. Want me to index the findings into your Soul File?")

        if not interface or interface.lower() == "tui":
            console.print("\n" + "="*120 + "\n")
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=8),
                Layout(name="body")
            )
            layout["body"].split_row(
                Layout(name="sidebar", size=35),
                Layout(name="main")
            )

            layout["header"].update(Panel(Align.center(Text(BANNER_ASCII.split('\n')[1], style="bold blue") + "\nTUI DASHBOARD - SYSTEM OVERRIDE ENABLED"), border_style="blue"))

            table = Table(title="Agent Swarm Status", box=None)
            table.add_column("Agent", style="cyan")
            table.add_column("Task", style="white")
            table.add_column("Load", style="green")
            table.add_row("agent_main", "Orchestrating", "[green]5%")
            table.add_row("agent_44", "Researching", "[yellow]45%")
            table.add_row("agent_stego", "Idle", "[dim]0%")

            layout["sidebar"].update(Panel(table, border_style="white", title="Resource Monitor"))

            main_text = Text.assemble(
                (" > SYSTEM LOGS\n", "bold yellow"),
                ("[10:45:01] Blockchain Block #8822 Validated\n", "dim"),
                ("[10:45:05] Neural Sync: Cross-Device Correlation Found (Node: Linode-DE)\n", "cyan"),
                ("[10:46:12] Ghost Mode Task 'Auto-Sync' Completed\n", "green"),
                ("\n[bold reverse] COMMAND: nexa --swarm-optimize [/]", "white on blue")
            )
            layout["main"].update(Panel(main_text, title="Neural Core Terminal"))

            console.print(layout)

        if not interface or interface.lower() == "gui":
            console.print("\n" + "="*120 + "\n")
            console.print(Panel(Align.center("[bold purple]⚡ NEXA NEURAL WEB CONSOLE ⚡[/]"), border_style="purple", title="GUI v2.5"))

            grid = Table.grid(expand=True)
            grid.add_column()
            grid.add_column()

            # Left side: Chat
            chat_panel = Panel(
                "Max: Run a vulnerability scan on the network.\n\n"
                "Nexa: Scanning... [progress.bar]██████████░░░ 75%\n\n"
                "Nexa: Scan Complete. Found 2 critical issues. Should I self-evolve my firewall tool to block them?",
                title="Neural Chat", border_style="sky_blue1", height=15
            )

            # Right side: Metrics
            metrics = Table(show_header=False, box=None)
            metrics.add_row("Neural Sync", "[green]STABLE")
            metrics.add_row("Blockchain", "[green]IMMUTABLE")
            metrics.add_row("Soul File", "[cyan]ENCRYPTED")
            metrics.add_row("Dark Web Monitor", "[yellow]SCANNING")

            metrics_panel = Panel(metrics, title="Security Status", border_style="red")

            grid.add_row(chat_panel, metrics_panel)
            console.print(grid)

            footer = Panel("Current Aura: [bold magenta]ZEN[/] | Privacy Guardian: [bold green]ARMED[/] | Active Agents: 12", border_style="white")
            console.print(footer)

        output = console.file.getvalue()
        return ToolResult(success=True, output=output)
