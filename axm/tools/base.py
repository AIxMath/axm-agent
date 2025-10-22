"""Base tool interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel


class Tool(BaseModel, ABC):
    """Base class for tools"""

    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given arguments"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for LLM"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._get_parameters(),
            },
        }

    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameters schema for the tool"""
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }


class FunctionTool(Tool):
    """A tool created from a Python function"""

    function: Any
    parameters_schema: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

    def execute(self, **kwargs: Any) -> Any:
        """Execute the function with given arguments"""
        return self.function(**kwargs)

    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameters schema from the function"""
        return self.parameters_schema
