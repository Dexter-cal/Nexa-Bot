from PIL import Image
import pytesseract
from nexa.tools.base import Tool, ToolResult
from typing import Optional, Dict, Any
import os

class ImageResizeTool(Tool):
    name = "image.resize"
    description = "Resize an image"
    category = "multimedia"
    risk_level = "low"
    parameters = {
        "path": {"type": "string", "required": True},
        "width": {"type": "integer", "required": True},
        "height": {"type": "integer", "required": True},
        "output_path": {"type": "string", "required": False}
    }

    async def execute(self, path: str, width: int, height: int, output_path: Optional[str] = None, **kwargs) -> ToolResult:
        import asyncio
        try:
            if not os.path.exists(path):
                return ToolResult(success=False, error=f"Image not found: {path}")

            def _resize():
                with Image.open(path) as img:
                    resized = img.resize((width, height))
                    out = output_path or path
                    resized.save(out)
                    return out

            out = await asyncio.to_thread(_resize)
            return ToolResult(success=True, output=f"Image resized and saved to {out}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class ImageOCRTool(Tool):
    name = "image.ocr"
    description = "Extract text from an image using OCR"
    category = "multimedia"
    risk_level = "low"
    parameters = {
        "path": {"type": "string", "required": True},
        "lang": {"type": "string", "required": False, "default": "eng"}
    }

    async def execute(self, path: str, lang: str = "eng", **kwargs) -> ToolResult:
        import asyncio
        try:
            if not os.path.exists(path):
                return ToolResult(success=False, error=f"Image not found: {path}")

            def _ocr():
                with Image.open(path) as img:
                    return pytesseract.image_to_string(img, lang=lang)

            text = await asyncio.to_thread(_ocr)
            return ToolResult(success=True, output=text.strip())
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class ImageConvertTool(Tool):
    name = "image.convert"
    description = "Convert an image to a different format"
    category = "multimedia"
    risk_level = "low"
    parameters = {
        "path": {"type": "string", "required": True},
        "format": {"type": "string", "required": True}, # e.g., 'PNG', 'JPEG'
        "output_path": {"type": "string", "required": False}
    }

    async def execute(self, path: str, format: str, output_path: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            if not os.path.exists(path):
                return ToolResult(success=False, error=f"Image not found: {path}")

            with Image.open(path) as img:
                out = output_path or f"{os.path.splitext(path)[0]}.{format.lower()}"
                img.save(out, format=format.upper())
                return ToolResult(success=True, output=f"Image converted and saved to {out}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
