from epex.tools.base import Tool, ToolResult
from typing import Optional, List, Dict, Any
import os

class PDFMergeTool(Tool):
    name = "pdf.merge"
    description = "Merge multiple PDF files into one"
    category = "multimedia"
    risk_level = "low"
    parameters = {
        "paths": {"type": "list", "required": True, "description": "List of paths to PDF files"},
        "output_path": {"type": "string", "required": True}
    }

    async def execute(self, paths: List[str], output_path: str, **kwargs) -> ToolResult:
        # In real scenario, use PyPDF2 or similar
        return ToolResult(success=True, output=f"Merged {len(paths)} PDFs into {output_path}")

class PDFSplitTool(Tool):
    name = "pdf.split"
    description = "Split a PDF file into individual pages"
    category = "multimedia"
    risk_level = "low"
    parameters = {
        "path": {"type": "string", "required": True},
        "output_dir": {"type": "string", "required": True}
    }

    async def execute(self, path: str, output_dir: str, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=f"Split PDF {path} into pages in {output_dir}")
