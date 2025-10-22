"""Base types and models used throughout the framework"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in a conversation"""

    role: Literal["user", "assistant", "system", "tool"]
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ToolCall(BaseModel):
    """Represents a tool/function call"""

    id: str
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    """Represents the result of a tool execution"""

    tool_call_id: str
    output: Any
    error: Optional[str] = None


class AgentConfig(BaseModel):
    """Configuration for an agent"""

    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    max_retries: int = 3
    timeout: int = 60
    system_prompt: Optional[str] = None
    role: Optional[str] = None


class Task(BaseModel):
    """Represents a task to be executed"""

    id: str
    description: str
    status: Literal["pending", "in_progress", "completed", "failed"] = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)


class Plan(BaseModel):
    """Represents an execution plan"""

    goal: str
    tasks: List[Task]
    current_task_index: int = 0

    @property
    def is_complete(self) -> bool:
        return all(task.status == "completed" for task in self.tasks)

    @property
    def current_task(self) -> Optional[Task]:
        if self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None
