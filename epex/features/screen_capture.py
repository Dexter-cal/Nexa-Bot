import asyncio
from PIL import Image
import os

# Mock mss for headless environment
try:
    import mss
except ImportError:
    mss = None

class ScreenCapture:
    """
    Capture screenshots
    """
    def __init__(self):
        if mss:
            self.sct = mss.mss()
            self.monitor = self.sct.monitors[1] if len(self.sct.monitors) > 1 else self.sct.monitors[0]
        else:
            self.sct = None

    async def capture(self) -> Image.Image:
        if not self.sct:
            # Return a blank image as fallback
            return Image.new('RGB', (1920, 1080), color='black')

        screenshot = self.sct.grab(self.monitor)
        return Image.frombytes('RGB', screenshot.size, screenshot.rgb)
