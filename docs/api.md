# API Reference

Complete API reference for AXM Agent.

## Core Module

### Agent

Main class for creating and managing AI agents.

```python
from axm import Agent

agent = Agent(
    model="gpt-4",                    # Model name or LLMProvider instance
    temperature=0.7,                   # Temperature (0-1)
    max_tokens=None,                   # Max tokens to generate
    max_retries=3,                     # Max retry attempts
    timeout=60,                        # Timeout in seconds
    system_prompt=None,                # System prompt
    role=None,                         # Role for multi-agent
    memory=None,                       # ConversationMemory instance
    mcp_server=None,                   # MCPServer instance
    api_key=None,                      # API key for provider
)
```

**Methods:**

- `run(prompt, response_format=None, max_iterations=10)` - Run agent synchronously
- `arun(prompt, response_format=None, max_iterations=10)` - Run agent asynchronously
- `stream(prompt)` - Stream response synchronously
- `astream(prompt)` - Stream response asynchronously
- `tool(func=None, *, name=None, description=None)` - Decorator to register tools
- `add_tool(tool)` - Add a Tool instance or callable
- `reset()` - Reset conversation memory
- `get_history()` - Get conversation history

### PlanningAgent

Agent that can decompose tasks and execute them.

```python
from axm import PlanningAgent

agent = PlanningAgent("gpt-4")
```

**Methods:**

- `create_plan(goal)` - Create execution plan for a goal
- `execute_task(task)` - Execute a single task
- `execute_plan(goal, verbose=True)` - Create and execute plan

### MultiAgent

System for coordinating multiple agents.

```python
from axm import MultiAgent

team = MultiAgent(
    agents=[agent1, agent2],          # List of agents
    orchestrator_model="gpt-4"        # Model for orchestrator
)
```

**Methods:**

- `collaborate(task, max_rounds=3, verbose=True)` - Coordinate agents on a task
- `add_agent(agent, role=None)` - Add an agent to the team
- `get_agent(role)` - Get agent by role

## Decorators

### @tool

Mark a function as a tool.

```python
from axm import tool

@tool
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"

@tool(name="custom_name", description="Custom description")
def another_tool(x: int) -> int:
    return x * 2
```

### @agent.tool

Register a tool with a specific agent.

```python
agent = Agent("gpt-4")

@agent.tool
def agent_tool(param: str) -> str:
    """Tool for this agent"""
    return param
```

### @validate_output

Validate function output with Pydantic.

```python
from axm.core.decorators import validate_output
from pydantic import BaseModel

class Output(BaseModel):
    result: str
    score: float

@validate_output(Output)
def process(data: str) -> dict:
    return {"result": data, "score": 0.95}
```

### @retry

Retry function on failure.

```python
from axm.core.decorators import retry

@retry(max_attempts=3, exceptions=(ValueError, ConnectionError))
def unstable_function():
    # May fail and retry
    pass
```

## LLM Providers

### LLMProvider

Base class for LLM providers.

```python
from axm.llm.base import LLMProvider

class CustomLLM(LLMProvider):
    def generate(self, messages, **kwargs):
        pass

    async def agenerate(self, messages, **kwargs):
        pass

    def stream(self, messages, **kwargs):
        pass

    async def astream(self, messages, **kwargs):
        pass
```

### OpenAIProvider

OpenAI LLM provider.

```python
from axm.llm import OpenAIProvider

provider = OpenAIProvider(
    api_key="your-key",
    base_url=None  # Optional custom base URL
)
```

### AnthropicProvider

Anthropic Claude provider.

```python
from axm.llm import AnthropicProvider

provider = AnthropicProvider(
    api_key="your-key",
    base_url=None
)
```

## Memory

### ConversationMemory

Manages conversation history.

```python
from axm.memory import ConversationMemory

memory = ConversationMemory(
    max_messages=None  # Max messages to keep (None for unlimited)
)
```

**Methods:**

- `add_message(message)` - Add message to memory
- `clear()` - Clear all messages
- `get_last_n(n)` - Get last n messages
- `filter_by_role(role)` - Get messages by role
- `__len__()` - Get message count
- `__getitem__(index)` - Get message by index

## MCP Support

### MCPServer

Model Context Protocol server for tool management.

```python
from axm.mcp import MCPServer

mcp = MCPServer(
    name="my-server",
    version="1.0.0"
)
```

**Methods:**

- `tool(func=None, *, name=None, description=None)` - Register tool
- `add_tool(tool)` - Add Tool instance
- `get_tools()` - Get all tools
- `get_tool(name)` - Get tool by name
- `execute_tool(name, **kwargs)` - Execute tool
- `add_resource(name, resource)` - Add resource
- `get_resource(name)` - Get resource
- `list_tools()` - List tool metadata
- `to_dict()` - Convert to dictionary

## Tools

### Tool

Base class for tools.

```python
from axm.tools import Tool

class CustomTool(Tool):
    name: str = "my_tool"
    description: str = "My custom tool"

    def execute(self, **kwargs):
        return "result"
```

### FunctionTool

Tool created from a function.

```python
from axm.tools import FunctionTool

tool = FunctionTool(
    name="my_function",
    description="Does something",
    function=my_func,
    parameters_schema={
        "type": "object",
        "properties": {...},
        "required": [...]
    }
)
```

## Types

### Message

Represents a conversation message.

```python
from axm.core.types import Message

msg = Message(
    role="user",              # "user", "assistant", "system", "tool"
    content="Hello",          # Message content
    name=None,                # Optional name
    tool_calls=None,          # Tool calls (for assistant)
    tool_call_id=None         # Tool call ID (for tool results)
)
```

### Task

Represents a task in a plan.

```python
from axm.core.types import Task

task = Task(
    id="task_1",
    description="Do something",
    status="pending",         # "pending", "in_progress", "completed", "failed"
    result=None,
    error=None,
    dependencies=[]
)
```

### Plan

Represents an execution plan.

```python
from axm.core.types import Plan

plan = Plan(
    goal="Accomplish something",
    tasks=[task1, task2],
    current_task_index=0
)
```

**Properties:**

- `is_complete` - Whether all tasks are complete
- `current_task` - Current task to execute

### AgentConfig

Agent configuration.

```python
from axm.core.types import AgentConfig

config = AgentConfig(
    model="gpt-4",
    temperature=0.7,
    max_tokens=None,
    max_retries=3,
    timeout=60,
    system_prompt=None,
    role=None
)
```

## Structured Output

Use Pydantic models for structured output:

```python
from axm import Agent
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str
    age: int = Field(gt=0, lt=150)
    occupation: str

agent = Agent("gpt-4")
person = agent.run(
    "Create a person profile",
    response_format=Person
)

print(person.name)
print(person.age)
```

## Async Support

All agent methods have async versions:

```python
import asyncio
from axm import Agent

async def main():
    agent = Agent("gpt-4")

    # Async run
    result = await agent.arun("Hello")

    # Async stream
    async for chunk in agent.astream("Tell me a story"):
        print(chunk, end="")

asyncio.run(main())
```

## Error Handling

```python
from axm import Agent

agent = Agent("gpt-4", max_retries=3, timeout=30)

try:
    response = agent.run("Hello")
except RuntimeError as e:
    print(f"Max iterations reached: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Environment Variables

Set API keys via environment variables:

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

Or in code:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-key"
```

Or pass directly:

```python
agent = Agent("gpt-4", api_key="your-key")
```

## Best Practices

1. **Use type hints** - Helps with validation and IDE support
2. **Write clear tool descriptions** - Helps LLM understand when to use tools
3. **Test tools separately** - Ensure tools work before adding to agents
4. **Use structured output** - For reliable data extraction
5. **Set reasonable limits** - max_iterations, max_tokens, timeout
6. **Handle errors** - Use try/except for production code
7. **Monitor usage** - Keep track of API calls and tokens
