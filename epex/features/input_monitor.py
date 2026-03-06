import asyncio
from typing import Callable, Optional

try:
    from pynput import mouse, keyboard
except ImportError:
    mouse = None
    keyboard = None

class InputMonitor:
    """
    Monitor mouse and keyboard inputs
    """
    def __init__(self):
        self.mouse_listener = None
        self.keyboard_listener = None
        self.on_click_callback = None
        self.on_key_callback = None

    async def start(self, on_click: Optional[Callable] = None, on_key: Optional[Callable] = None):
        if not mouse or not keyboard:
            print("pynput not available - input monitoring disabled")
            return

        self.on_click_callback = on_click
        self.on_key_callback = on_key

        self.mouse_listener = mouse.Listener(on_click=self._handle_click)
        self.mouse_listener.start()

        self.keyboard_listener = keyboard.Listener(on_press=self._handle_key)
        self.keyboard_listener.start()

    def _handle_click(self, x, y, button, pressed):
        if self.on_click_callback:
            self.on_click_callback(x, y, str(button), pressed)

    def _handle_key(self, key):
        if self.on_key_callback:
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key)
            self.on_key_callback(key_str)

    async def stop(self):
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
