import asyncio
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from epex.tools.registry import registry

logger = logging.getLogger(__name__)

class ToolHub:
    """
    Interface for browsing and launching EPEX tools
    """
    def __init__(self):
        self.console = Console()

    async def run(self):
        await registry.load_default_tools()

        while True:
            self.console.clear()
            self.console.print(Panel("[bold cyan]🚀 EPEX APEX TOOL HUB[/]", border_style="cyan"))

            table = Table(title="Available Tools")
            table.add_column("#", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Category", style="magenta")
            table.add_column("Description")
            table.add_column("Risk", style="red")

            all_tools = registry.list_all()
            for i, tool in enumerate(all_tools):
                table.add_row(str(i+1), tool.name, tool.category, tool.description[:60] + "...", tool.risk_level)

            self.console.print(table)
            self.console.print("\n[dim]Type tool number to view details/launch, or 'exit' to return.[/]")

            choice = Prompt.ask("Select a tool")
            if choice.lower() == 'exit':
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(all_tools):
                    await self.inspect_tool(all_tools[idx])
            except ValueError:
                self.console.print("[red]Invalid selection.[/]")
                await asyncio.sleep(1)

    async def inspect_tool(self, tool):
        self.console.clear()
        self.console.print(Panel(f"[bold cyan]Tool: {tool.name}[/]\n\n{tool.description}\n\n[bold]Risk Level:[/] {tool.risk_level}\n[bold]Parameters:[/] {tool.parameters}", border_style="cyan"))

        launch = Prompt.ask("\nLaunch this tool?", choices=["y", "n"], default="n")
        if launch.lower() == 'y':
            params = {}
            for p_name, p_info in tool.parameters.items():
                val = Prompt.ask(f"Enter {p_name} ({p_info.get('description', '')})")
                params[p_name] = val

            with self.console.status(f"[bold green]Executing {tool.name}..."):
                result = await tool.execute(**params)

            self.console.print(Panel(str(result.output) if result.success else f"[red]Error: {result.error}[/]", title="Execution Result"))
            Prompt.ask("\nPress Enter to return")
