"""Tests for the core Agent functionality"""

from axm import Agent
from axm.core.types import Message
from axm.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing"""

    def __init__(self, response_text: str = "Mock response"):
        self.response_text = response_text
        self.generate_call_count = 0

    def generate(self, messages, **kwargs):
        self.generate_call_count += 1
        return Message(role="assistant", content=self.response_text)

    async def agenerate(self, messages, **kwargs):
        self.generate_call_count += 1
        return Message(role="assistant", content=self.response_text)

    def stream(self, messages, **kwargs):
        yield self.response_text

    async def astream(self, messages, **kwargs):
        yield self.response_text


def test_agent_initialization():
    """Test basic agent initialization"""
    mock_llm = MockLLMProvider()
    agent = Agent(mock_llm)

    assert agent.llm == mock_llm
    assert agent.config.model == "custom"
    assert agent.memory.messages == []


def test_agent_with_system_prompt():
    """Test agent with system prompt"""
    mock_llm = MockLLMProvider()
    system_prompt = "You are a helpful assistant"
    agent = Agent(mock_llm, system_prompt=system_prompt)

    assert len(agent.memory.messages) == 1
    assert agent.memory.messages[0].content == system_prompt


def test_tool_decorator():
    """Test tool decorator functionality"""
    mock_llm = MockLLMProvider()
    agent = Agent(mock_llm)

    @agent.tool
    def test_tool(param: str) -> str:
        """A test tool"""
        return f"Test: {param}"

    # Check if tool was registered
    assert "test_tool" in agent.tools
    tool = agent.tools["test_tool"]
    assert tool.description == "A test tool"

    # Check if tool can be executed
    result = tool.execute(param="hello")
    assert result == "Test: hello"


def test_agent_run():
    """Test basic agent run functionality"""
    mock_llm = MockLLMProvider("Test response")
    agent = Agent(mock_llm)

    response = agent.run("Hello")
    assert response == "Test response"
    assert mock_llm.generate_call_count == 1

    # Check if user message was added to memory
    assert len(agent.memory.messages) == 2
    assert agent.memory.messages[-2].content == "Hello"


def test_agent_with_tool_execution():
    """Test agent with tool execution"""
    mock_llm = MockLLMProvider("Tool result received")
    agent = Agent(mock_llm)

    # Add a tool that should be called
    @agent.tool
    def get_info(topic: str) -> str:
        return f"Information about {topic}"

    # Mock the LLM to respond with a tool call first, then a final response
    mock_llm.response_text = "I got the information"

    def mock_generate(messages, **kwargs):
        if mock_llm.generate_call_count == 0:
            # First call - return tool call
            return Message(
                role="assistant",
                content="",
                tool_calls=[
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "get_info", "arguments": '{"topic": "AI"}'},
                    }
                ],
            )
        else:
            # Second call - return final response
            return Message(role="assistant", content="I got the information")

    mock_llm.generate = mock_generate

    response = agent.run("Tell me about AI")
    assert response == "I got the information"
    assert mock_llm.generate_call_count == 2


def test_agent_reset():
    """Test agent memory reset"""
    mock_llm = MockLLMProvider()
    agent = Agent(mock_llm, system_prompt="System message")

    # Add some messages
    agent.run("Hello")
    agent.run("How are you?")

    # Should have system + 2 messages
    assert len(agent.memory.messages) == 3

    # Reset should keep system message
    agent.reset()
    assert len(agent.memory.messages) == 1
    assert agent.memory.messages[0].content == "System message"
