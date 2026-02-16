import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from nexa.features.screen_capture import ScreenCapture
from nexa.features.input_monitor import InputMonitor
from nexa.features.playback_engine import PlaybackEngine

class TeachMode:
    """
    Record user workflows by watching their actions
    """
    def __init__(self):
        self.recording = False
        self.workflow_name = None
        self.actions = []
        self.screen_capture = ScreenCapture()
        self.input_monitor = InputMonitor()
        self.playback_engine = PlaybackEngine()
        self.workflows_dir = Path.home() / '.nexa' / 'workflows'
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

    async def start_recording(self, workflow_name: str):
        if self.recording: return
        self.recording = True
        self.workflow_name = workflow_name
        self.actions = []

        await self.input_monitor.start(on_click=self._on_click, on_key=self._on_key)
        print(f"📹 Recording workflow: {workflow_name}...")

    def _on_click(self, x, y, button, pressed):
        if pressed and self.recording:
            self.actions.append({'type': 'click', 'x': x, 'y': y, 'button': button, 'timestamp': datetime.now().isoformat()})

    def _on_key(self, key):
        if self.recording:
            self.actions.append({'type': 'key', 'key': key, 'timestamp': datetime.now().isoformat()})

    async def stop_recording(self) -> Dict:
        if not self.recording: return {}
        self.recording = False
        await self.input_monitor.stop()

        workflow = {
            'name': self.workflow_name,
            'created_at': datetime.now().isoformat(),
            'steps': self._process_actions()
        }

        with open(self.workflows_dir / f"{self.workflow_name}.json", 'w') as f:
            json.dump(workflow, f, indent=2)

        print(f"✓ Workflow '{self.workflow_name}' saved.")
        return workflow

    def _process_actions(self) -> List[Dict]:
        steps = []
        current_typing = None

        for action in self.actions:
            if action['type'] == 'click':
                if current_typing:
                    steps.append(current_typing)
                    current_typing = None
                steps.append({'action': 'click', 'x': action['x'], 'y': action['y']})
            elif action['type'] == 'key':
                if not current_typing:
                    current_typing = {'action': 'type', 'keys': []}
                current_typing['keys'].append(action['key'])

        if current_typing:
            steps.append(current_typing)
        return steps

    async def play_workflow(self, name: str):
        workflow_path = self.workflows_dir / f"{name}.json"
        if not workflow_path.exists():
            print(f"Workflow {name} not found.")
            return
        with open(workflow_path) as f:
            workflow = json.load(f)
        await self.playback_engine.play(workflow)
