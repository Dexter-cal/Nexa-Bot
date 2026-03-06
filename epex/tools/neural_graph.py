import logging
import json
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
import io

logger = logging.getLogger(__name__)

class NeuralGraphTool(Tool):
    name = "meta.neural_graph"
    description = "Generate a visual tree/graph of Epex's current reasoning and thought chain."
    category = "meta"
    risk_level = "low"
    parameters = {
        "depth": {"type": "integer", "required": False, "default": 2}
    }

    async def execute(self, depth: int = 2, **kwargs) -> ToolResult:
        from epex.core.engine import engine

        # Pull logs from StrategicPlanner
        logs = engine.task_manager.planner.reasoning_logs
        if not logs:
            return ToolResult(success=True, output="No reasoning logs found. Run a task first.")

        latest_log = logs[-1]
        goal = latest_log.get('goal', 'Unknown Goal')

        console = Console(file=io.StringIO(), force_terminal=True, width=80)

        tree = Tree(f"🧠 [bold cyan]Neural Thought Graph[/]: {goal}")

        # Simplified tree representation of the reasoning
        # In a real app, we'd parse the LLM's internal thought chain

        node_context = tree.add("[yellow]User Context Analysis[/]")
        node_context.add(f"Aura: [magenta]{engine.soul.data.get('current_aura', 'professional')}[/]")
        node_context.add(f"Mood: [green]{engine.soul.data.get('current_mood', 'efficient')}[/]")

        node_planning = tree.add("[blue]Strategic Planning[/]")
        node_planning.add(f"Model selected: [white]{latest_log.get('model', 'auto')}[/]")

        node_exec = tree.add("[red]Execution Flow[/]")
        task_id = latest_log.get('task_id')
        checkpoints = engine.task_manager.task_checkpoints.get(task_id, [])
        for cp in checkpoints:
            node_exec.add(f"Step {cp['step_index']}: [dim]Checkpoint created[/]")

        console.print(Panel(tree, border_style="cyan"))

        output = console.file.getvalue()
        return ToolResult(success=True, output=output)
