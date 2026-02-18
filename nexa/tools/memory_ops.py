import os
import logging
from typing import Dict, Any, List
from nexa.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class MemoryIndexingTool(Tool):
    name = "memory.index_directory"
    description = "Recursively scan a directory and index its contents into long-term memory."
    category = "memory"
    risk_level = "medium"
    parameters = {
        "path": {"type": "string", "required": True, "description": "Local path to index"},
        "recursive": {"type": "boolean", "required": False, "default": True}
    }

    async def execute(self, path: str, recursive: bool = True, **kwargs) -> ToolResult:
        if not os.path.exists(path):
            return ToolResult(success=False, error=f"Path not found: {path}")

        logger.info(f"Indexing directory: {path}")
        from nexa.core.engine import engine
        memory = engine.memory

        count = 0
        for root, dirs, files in os.walk(path):
            if not recursive and root != path:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Basic file summary for memory
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read(1000) # Only first 1000 chars for context
                    await memory.add(f"File found in {path}: {file}. Content snippet: {content}")
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to index {file_path}: {e}")

        return ToolResult(success=True, output=f"Successfully indexed {count} files from {path} into long-term memory.")

class MemorySearchTool(Tool):
    name = "memory.search"
    description = "Search through Nexa's long-term vector memory for specific information."
    category = "memory"
    risk_level = "low"
    parameters = {
        "query": {"type": "string", "required": True}
    }

    async def execute(self, query: str, **kwargs) -> ToolResult:
        from nexa.core.engine import engine
        results = await engine.memory.search(query, limit=5)
        return ToolResult(success=True, output=results)
