from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class ToolResult(BaseModel):
    """Result of tool execution"""
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    logs: List[str] = []
    metadata: Dict[str, Any] = {}

class Tool(ABC):
    """Base class for all tools"""

    name: str
    description: str
    parameters: Dict[str, Any]
    risk_level: str = 'medium'
    category: str = 'general'

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass

    def validate(self, **kwargs) -> bool:
        """Validate parameters before execution"""
        required = [k for k, v in self.parameters.items() if v.get('required')]
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        return True
