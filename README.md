# 🤖 AXM Agent

**A simple, elegant Python framework for building AI agents with decorators, MCP support, and powerful utilities**

[![PyPI version](https://badge.fury.io/py/axm-agent.svg)](https://badge.fury.io/py/axm-agent)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Why AXM Agent?

AXM Agent is designed with **simplicity** and **developer experience** in mind. Unlike heavyweight frameworks, AXM Agent lets you build powerful AI agents with just a few lines of code using elegant decorators and intuitive APIs.

```python
from axm import Agent, tool

# Create an agent
agent = Agent("gpt-4")

# Define tools with a simple decorator
@agent.tool
def get_weather(city: str) -> str:
    """Get the weather for a city"""
    return f"Sunny in {city}"

# Run the agent
response = agent.run("What's the weather in Paris?")
print(response)
```

## 🚀 Features

- **🎯 Simple Decorator API** - Define tools and agents with intuitive decorators
- **🔌 MCP Support** - Full Model Context Protocol integration
- **📞 Function Calling** - Automatic function calling with type validation
- **📋 Planning & Scheduling** - Built-in task planning and execution
- **✅ Format-Constrained Output** - JSON, Pydantic models, and custom schemas
- **⚡ Async & Streaming** - Full async support with streaming responses
- **🎨 Multi-Agent Systems** - Easy collaboration between multiple agents
- **🔄 Memory & Context** - Conversation memory and context management
- **🛠️ Multiple LLM Support** - OpenAI, Anthropic, and custom providers
- **📊 Observable** - Built-in logging and tracing

## 📦 Installation

```bash
pip install axm-agent
```

For OpenAI support:
```bash
pip install axm-agent[openai]
```

For Anthropic (Claude) support:
```bash
pip install axm-agent[anthropic]
```

For all providers:
```bash
pip install axm-agent[all]
```

## 🎓 Quick Start

### Basic Agent

```python
from axm import Agent

agent = Agent("gpt-4")
response = agent.run("Tell me a joke")
print(response)
```

### Agent with Tools

```python
from axm import Agent, tool
import datetime

agent = Agent("gpt-4")

@agent.tool
def get_current_time() -> str:
    """Get the current time"""
    return datetime.datetime.now().strftime("%H:%M:%S")

@agent.tool
def calculate(expression: str) -> float:
    """Safely evaluate a mathematical expression"""
    return eval(expression, {"__builtins__": {}})

response = agent.run("What time is it and what is 25 * 4?")
print(response)
```

### Structured Output

```python
from axm import Agent
from pydantic import BaseModel

class WeatherReport(BaseModel):
    city: str
    temperature: float
    conditions: str
    humidity: int

agent = Agent("gpt-4")
report = agent.run(
    "Generate a weather report for Paris",
    response_format=WeatherReport
)
print(f"{report.city}: {report.temperature}°C, {report.conditions}")
```

### Planning Agent

```python
from axm import PlanningAgent

agent = PlanningAgent("gpt-4")

# The agent will break down the task into steps and execute them
result = agent.execute_plan(
    "Research the top 3 programming languages in 2025 and create a comparison"
)
```

### Multi-Agent System

```python
from axm import Agent, MultiAgent

researcher = Agent("gpt-4", role="researcher")
writer = Agent("gpt-4", role="writer")
critic = Agent("gpt-4", role="critic")

team = MultiAgent([researcher, writer, critic])
result = team.collaborate("Write an article about AI agents")
```

### Async Support

```python
from axm import Agent
import asyncio

async def main():
    agent = Agent("gpt-4")

    # Async execution
    response = await agent.arun("Tell me about async programming")

    # Streaming
    async for chunk in agent.stream("Write a story"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### MCP Integration

```python
from axm import Agent
from axm.mcp import MCPServer

# Create an MCP server
mcp = MCPServer()

@mcp.tool
def search_database(query: str) -> list:
    """Search the database"""
    return ["result1", "result2"]

# Connect agent to MCP
agent = Agent("gpt-4", mcp_server=mcp)
response = agent.run("Search for user data")
```

## 📚 Advanced Features

### Custom LLM Provider

```python
from axm import Agent, LLMProvider

class CustomLLM(LLMProvider):
    def generate(self, messages, **kwargs):
        # Your custom LLM logic
        pass

agent = Agent(CustomLLM())
```

### Memory Management

```python
from axm import Agent
from axm.memory import ConversationMemory

agent = Agent("gpt-4", memory=ConversationMemory(max_messages=10))

agent.run("My name is Alice")
agent.run("What's my name?")  # Will remember "Alice"
```

### Retry & Error Handling

```python
from axm import Agent

agent = Agent("gpt-4", max_retries=3, timeout=30)

@agent.tool
def risky_operation() -> str:
    """An operation that might fail"""
    # Will automatically retry on failure
    pass
```

## 🏗️ Architecture

AXM Agent is built on three core principles:

1. **Simplicity First** - Easy things should be easy, complex things should be possible
2. **Type Safety** - Full Pydantic integration for validation
3. **Composability** - Mix and match components to build what you need

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Inspired by the best ideas from LangChain, CrewAI, and AutoGen, but designed for simplicity.

## 📖 Documentation

For full documentation, visit [our docs](https://github.com/yourusername/axm-agent/docs)

## 🐛 Issues

Found a bug? Please [open an issue](https://github.com/yourusername/axm-agent/issues)
