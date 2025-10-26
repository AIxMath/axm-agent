# Getting Started with AXM Agent

Welcome to AXM Agent! This guide will help you get up and running quickly.

## Installation

```bash
pip install axm-agent
```

For specific LLM providers:

```bash
# For OpenAI (GPT-4, GPT-3.5, etc.)
pip install axm-agent[openai]

# For Anthropic (Claude)
pip install axm-agent[anthropic]

# For all providers
pip install axm-agent[all]
```

## Configuration

### Environment Variables

AXM Agent uses dedicated environment variables for each provider:

**OpenAI:**
```bash
export AXM_OPENAI_API_KEY="sk-..."
```

**Anthropic (Claude):**
```bash
export AXM_ANTHROPIC_API_KEY="sk-ant-..."
```

**OpenAI-Compatible Providers (DeepSeek, Groq, local LLMs, etc.):**
```bash
export AXM_OPENAI_COMPATIBLE_API_KEY="your-api-key"
export AXM_OPENAI_COMPATIBLE_BASE_URL="https://your-endpoint.com/v1"
```

### Passing Credentials Directly

You can also pass credentials directly when creating agents:

```python
from axm import Agent

# OpenAI
agent = Agent("gpt-4", api_key="sk-...")

# OpenAI-compatible endpoint
agent = Agent(
    "deepseek-v3",
    api_key="your-api-key",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# Anthropic
agent = Agent("claude-3-opus-20240229", api_key="sk-ant-...")
```

## Basic Setup

```python
from axm import Agent

# Create an agent with GPT-4
agent = Agent("gpt-4")

# Use the agent
response = agent.run("Tell me a joke")
print(response)
```

## Core Concepts

### Agents

Agents are the main interface for interacting with LLMs. They maintain conversation history and can use tools.

```python
from axm import Agent

# Basic agent
agent = Agent("gpt-4")

# Agent with configuration
agent = Agent(
    "gpt-4",
    temperature=0.7,
    max_tokens=500,
    system_prompt="You are a helpful coding assistant"
)
```

### Tools

Tools are functions that agents can call to perform actions or retrieve information.

```python
from axm import Agent

agent = Agent("gpt-4")

@agent.tool
def get_weather(city: str) -> str:
    """Get the weather for a city"""
    # In real use, call a weather API
    return f"Sunny in {city}"

@agent.tool
def calculate(expression: str) -> float:
    """Calculate a mathematical expression"""
    return eval(expression, {"__builtins__": {}})

# The agent can now use these tools
response = agent.run("What's the weather in Paris and what is 10 * 5?")
```

### Structured Output

Get structured, validated output using Pydantic models:

```python
from axm import Agent
from pydantic import BaseModel

class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    prep_time: int

agent = Agent("gpt-4")
recipe = agent.run(
    "Create a recipe for chocolate chip cookies",
    response_format=Recipe
)

print(f"Recipe: {recipe.name}")
print(f"Prep time: {recipe.prep_time} minutes")
```

### Planning Agent

For complex tasks that need to be broken down:

```python
from axm import PlanningAgent

agent = PlanningAgent("gpt-4")

result = agent.execute_plan(
    "Research Python web frameworks and create a comparison",
    verbose=True
)
```

### Multi-Agent Systems

Multiple agents working together:

```python
from axm import Agent, MultiAgent

researcher = Agent("gpt-4", role="researcher")
writer = Agent("gpt-4", role="writer")
editor = Agent("gpt-4", role="editor")

team = MultiAgent([researcher, writer, editor])
result = team.collaborate("Write an article about AI agents")
```

### MCP Integration

Model Context Protocol for tool management:

```python
from axm import Agent, MCPServer

# Create MCP server
mcp = MCPServer()

@mcp.tool
def search_db(query: str) -> list:
    """Search database"""
    return ["result1", "result2"]

# Connect to agent
agent = Agent("gpt-4", mcp_server=mcp)
```

### Async & Streaming

Full async support:

```python
import asyncio
from axm import Agent

async def main():
    agent = Agent("gpt-4")

    # Async execution
    response = await agent.arun("Tell me about Python")

    # Streaming
    async for chunk in agent.astream("Write a story"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## Common Patterns

### 1. Agent with Memory Management

```python
from axm import Agent
from axm.memory import ConversationMemory

# Keep only last 10 messages
agent = Agent("gpt-4", memory=ConversationMemory(max_messages=10))

agent.run("My name is Alice")
agent.run("What's my name?")  # Will remember "Alice"
```

### 2. Retry on Failure

```python
from axm import Agent
from axm.core.decorators import retry

agent = Agent("gpt-4")

@retry(max_attempts=3)
@agent.tool
def unstable_api_call(param: str) -> str:
    """Call an unstable API"""
    # Will retry up to 3 times on failure
    return call_api(param)
```

### 3. Custom LLM Provider

```python
from axm import Agent, LLMProvider
from axm.core.types import Message

class CustomLLM(LLMProvider):
    def generate(self, messages, **kwargs):
        # Your custom logic
        return Message(role="assistant", content="Response")

    async def agenerate(self, messages, **kwargs):
        return Message(role="assistant", content="Response")

    def stream(self, messages, **kwargs):
        yield "Response"

    async def astream(self, messages, **kwargs):
        yield "Response"

agent = Agent(CustomLLM())
```

## Examples

Check out the `examples/` directory for complete examples:

- `basic_agent.py` - Basic agent with tools
- `structured_output.py` - Using Pydantic models
- `planning_agent.py` - Complex task planning
- `multi_agent.py` - Multi-agent collaboration
- `mcp_server.py` - MCP integration
- `async_streaming.py` - Async and streaming

## Next Steps

- Read the [API Documentation](docs/api.md)
- Check out [Advanced Usage](docs/advanced.md)
- Join our [Community](https://github.com/AIxMath/axm-agent/discussions)

## Tips

1. **Start Simple**: Begin with a basic agent and add tools as needed
2. **Use Type Hints**: Type hints help with validation and IDE support
3. **Test Tools Separately**: Test your tools independently before adding to agents
4. **Monitor Token Usage**: Keep track of your LLM usage
5. **Use Structured Output**: For reliable data extraction, use Pydantic models

## Troubleshooting

### API Key Issues

```python
# Check if key is set
import os
print(os.getenv("AXM_OPENAI_API_KEY"))
print(os.getenv("AXM_ANTHROPIC_API_KEY"))
print(os.getenv("AXM_OPENAI_COMPATIBLE_API_KEY"))

# Or pass directly
agent = Agent("gpt-4", api_key="your-key")
```

### Import Errors

Make sure you've installed the correct extras:

```bash
pip install axm-agent[openai]  # For OpenAI
pip install axm-agent[anthropic]  # For Anthropic
```

### Tool Not Being Called

Ensure:
1. Tool has a good description
2. Tool name is clear
3. Parameters have type hints
4. You're using a model that supports function calling

## Getting Help

- GitHub Issues: [Report bugs](https://github.com/AIxMath/axm-agent/issues)
- Discussions: [Ask questions](https://github.com/AIxMath/axm-agent/discussions)
- Documentation: [Full docs](docs/)
