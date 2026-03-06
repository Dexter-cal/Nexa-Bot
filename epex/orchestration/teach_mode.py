import time
import asyncio
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class WorkflowStep:
    def __init__(self, action_type: str, target: str, value: Any = None, timestamp: float = None):
        self.action_type = action_type
        self.target = target
        self.value = value
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        return {
            "action_type": self.action_type,
            "target": self.target,
            "value": self.value,
            "timestamp": self.timestamp
        }

class TeachMode:
    """
    Record and replay user actions to create reusable workflows
    """
    def __init__(self):
        self.is_recording = False
        self.current_workflow: List[WorkflowStep] = []
        self.workflow_name: Optional[str] = None

    async def start_recording(self, name: str):
        self.is_recording = True
        self.workflow_name = name
        self.current_workflow = []
        logger.info(f"Started recording workflow: {name}")

    def record_action(self, action_type: str, target: str, value: Any = None):
        if self.is_recording:
            step = WorkflowStep(action_type, target, value)
            self.current_workflow.append(step)
            logger.debug(f"Recorded action: {action_type} on {target}")

    async def stop_recording(self) -> Dict[str, Any]:
        self.is_recording = False
        workflow = {
            "name": self.workflow_name,
            "steps": [step.to_dict() for step in self.current_workflow],
            "created_at": time.time()
        }
        logger.info(f"Stopped recording workflow: {self.workflow_name}")
        return workflow

    async def replay_workflow(self, workflow: Dict[str, Any]):
        logger.info(f"Replaying workflow: {workflow['name']}")
        steps = workflow.get("steps", [])

        from epex.tools.registry import registry

        for step in steps:
            logger.info(f"Replaying step: {step['action_type']} on {step['target']}")

            # Use vision to confirm state if needed
            vision_tool = registry.get("system.vision_analyze")
            if vision_tool:
                await vision_tool.execute(prompt=f"Confirm if {step['target']} is visible on screen.")

            # Map action to tools
            if step['action_type'] == 'click':
                mouse = registry.get("system.mouse")
                if mouse: await mouse.execute(action="click", x=step.get('x'), y=step.get('y'))
            elif step['action_type'] == 'type':
                keyboard = registry.get("system.keyboard")
                if keyboard: await keyboard.execute(action="type", text=step.get('value'))

            await asyncio.sleep(1.0) # Realistic delay

        logger.info(f"Finished replaying workflow: {workflow['name']}")
