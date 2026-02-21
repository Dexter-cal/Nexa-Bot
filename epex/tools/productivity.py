import os
from epex.tools.base import Tool, ToolResult
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

class NoteTakingTool(Tool):
    name = "productivity.note"
    description = "Create or append to a note"
    category = "productivity"
    risk_level = "low"
    parameters = {
        "title": {"type": "string", "required": True},
        "content": {"type": "string", "required": True},
        "append": {"type": "boolean", "required": False, "default": False}
    }

    async def execute(self, title: str, content: str, append: bool = False, **kwargs) -> ToolResult:
        # For simplicity, we'll store notes in a local 'notes' directory
        notes_dir = "notes"
        if not os.path.exists(notes_dir):
            os.makedirs(notes_dir)

        file_path = os.path.join(notes_dir, f"{title}.txt")
        mode = 'a' if append else 'w'
        try:
            with open(file_path, mode) as f:
                if append: f.write("\n")
                f.write(content)
            return ToolResult(success=True, output=f"Note '{title}' saved successfully.")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class CalendarTool(Tool):
    name = "productivity.calendar"
    description = "Manage events in a simple calendar"
    category = "productivity"
    risk_level = "low"
    parameters = {
        "action": {"type": "string", "required": True}, # 'add', 'list', 'delete'
        "event": {"type": "string", "required": False},
        "date": {"type": "string", "required": False} # YYYY-MM-DD
    }

    _events = [] # In-memory calendar for now

    async def execute(self, action: str, event: Optional[str] = None, date: Optional[str] = None, **kwargs) -> ToolResult:
        if action == "add":
            if not event or not date:
                return ToolResult(success=False, error="Event and date required for adding.")
            self._events.append({"event": event, "date": date})
            return ToolResult(success=True, output=f"Event '{event}' added to {date}.")
        elif action == "list":
            return ToolResult(success=True, output=self._events)
        elif action == "delete":
            if not event: return ToolResult(success=False, error="Event title required for deletion.")
            self._events = [e for e in self._events if e['event'] != event]
            return ToolResult(success=True, output=f"Event '{event}' deleted.")
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")
