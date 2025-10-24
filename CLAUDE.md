# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AXM Agent is a Python framework for building AI agents with a decorator-based API, supporting OpenAI and Anthropic LLMs. The framework emphasizes simplicity and type safety with Pydantic integration.

## Development Commands

### Testing
```bash
# Run all tests with coverage
pytest tests/ -v --cov=axm --cov-report=xml

# Run a single test file
pytest tests/test_agent.py -v

# Run specific test
pytest tests/test_agent.py::test_function_name -v
```

### Linting & Formatting
```bash
# Check formatting (does not modify files)
black --check axm tests examples

# Format code
black axm tests examples

# Run linter (check only)
ruff check axm tests examples

# Run linter with auto-fix
ruff check axm tests examples --fix

# Type checking
mypy axm
```

### Installation for Development
```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install with specific provider support
pip install -e ".[openai]"
pip install -e ".[anthropic]"
pip install -e ".[all]"
```

## Architecture

### Core Components

**Agent System** (`axm/core/`):
- `Agent` - Base agent class with tool execution loop and memory management
- `PlanningAgent` - Extends Agent with task decomposition and dependency-aware execution
- `MultiAgent` - Orchestrates multiple agents with role-based collaboration

**LLM Providers** (`axm/llm/`):
- Abstract `LLMProvider` base class defines interface for all providers
- `OpenAIProvider` and `AnthropicProvider` implement provider-specific message formats
- Agent auto-detects provider from model name (e.g., "gpt-4" → OpenAI, "claude-" → Anthropic)
- Both providers support `base_url` parameter for custom endpoints

**Tool System** (`axm/tools/` and `axm/core/decorators.py`):
- Tools are registered via `@agent.tool` decorator
- Decorator automatically generates JSON schema from function signatures using Pydantic
- `FunctionTool` wraps Python functions with schema for LLM tool calling
- MCP (Model Context Protocol) integration via `MCPServer` for external tools

**Memory** (`axm/memory/`):
- `ConversationMemory` stores message history
- Agent maintains memory across `run()` calls for context
- System prompts persist through `reset()` operations

### Key Design Patterns

1. **Tool Execution Loop** (axm/core/agent.py:169-259):
   - Agent runs iterative loop handling tool calls
   - Each iteration: generate response → execute tool calls → add results to memory → continue
   - Max iterations prevents infinite loops
   - Tool results are added as "tool" role messages

2. **Provider Auto-detection** (axm/core/agent.py:72-86):
   - Agent constructor accepts string model names or LLMProvider instances
   - Model name prefix determines provider (gpt*/o1* → OpenAI, claude* → Anthropic)
   - API key and base_url are passed to selected provider

3. **Structured Output** (via response_format parameter):
   - Accepts Pydantic models as response_format
   - Providers inject schema into system prompt
   - OpenAI uses native JSON mode; Anthropic uses prompt engineering
   - Response parsed and validated against Pydantic model

4. **Planning & Execution** (axm/core/planning_agent.py):
   - PlanningAgent creates Plans with dependency graphs
   - Tasks executed in topological order respecting dependencies
   - Detects circular dependencies and failed prerequisites

5. **Multi-Agent Orchestration** (axm/core/multi_agent.py):
   - Orchestrator agent coordinates role-based agents
   - Uses special protocol: "ASSIGN <role>: <task>" for delegation
   - "FINAL:" prefix signals completion
   - Conversation history shared between rounds

### Message Flow

```
User Input → Agent.run()
  → Memory.add_message(user message)
  → Loop:
    → LLMProvider.generate(messages, tools)
    → Memory.add_message(assistant response)
    → If tool_calls:
        → Execute tools
        → Memory.add_message(tool results)
        → Continue loop
    → Else: Return content
```

### Type System

Core types in `axm/core/types.py`:
- `Message` - Unified message format supporting user/assistant/system/tool roles
- `AgentConfig` - Agent configuration (model, temperature, etc.)
- `Task` - Represents executable task with status and dependencies
- `Plan` - Collection of tasks with completion tracking

## Code Style

- Line length: 100 characters (black and ruff configured)
- Python 3.9+ compatibility required
- Type hints used but `mypy` not strictly enforced (continue-on-error in CI)
- Pydantic v2 for all data models

## Important Notes

### Adding New LLM Providers

1. Inherit from `LLMProvider` in axm/llm/base.py
2. Implement: `generate()`, `agenerate()`, `stream()`, `astream()`
3. Convert internal `Message` format to provider-specific format
4. Handle tool calls in provider-specific format
5. Accept `api_key` and `base_url` in constructor
6. Add to Agent auto-detection logic if desired

### Tool Registration

Tools are registered two ways:
1. **Decorator**: `@agent.tool` - uses `axm/core/decorators.py:tool()` to extract type hints
2. **Direct**: `agent.add_tool(Tool)` - accepts Tool instances

The `@agent.tool` decorator:
- Introspects function signature using `inspect`
- Generates Pydantic model from parameters
- Creates JSON schema for LLM
- Stores metadata on function object

### Memory Management

- `ConversationMemory` is simple list of Messages
- No automatic pruning - caller must manage via max_messages
- System messages preserved during `reset()`
- Tool messages must include `tool_call_id` to match LLM's tool calls

### Testing Strategy

- Unit tests in `tests/` directory
- Provider tests may be skipped if dependencies not installed (ImportError handling)
- Tests use mock API keys ("test-key") and custom base_urls
- Async tests use `pytest-asyncio` with `asyncio_mode = "auto"`
