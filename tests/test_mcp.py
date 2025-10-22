"""Tests for MCP Server"""

import pytest
from axm.mcp import MCPServer


def test_mcp_server_initialization():
    """Test MCP server initialization"""
    mcp = MCPServer(name="test-server", version="1.0.0")

    assert mcp.name == "test-server"
    assert mcp.version == "1.0.0"
    assert len(mcp.tools) == 0
    assert len(mcp.resources) == 0


def test_mcp_tool_registration():
    """Test tool registration with MCP server"""
    mcp = MCPServer()

    @mcp.tool
    def test_function(param: str) -> str:
        """A test function"""
        return f"Result: {param}"

    # Check if tool was registered
    assert "test_function" in mcp.tools
    assert len(mcp.tools) == 1

    # Check tool properties
    tool = mcp.get_tool("test_function")
    assert tool is not None
    assert tool.name == "test_function"
    assert tool.description == "A test function"


def test_mcp_tool_execution():
    """Test executing tools through MCP server"""
    mcp = MCPServer()

    @mcp.tool
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    result = mcp.execute_tool("add_numbers", a=5, b=3)
    assert result == 8


def test_mcp_resource_management():
    """Test resource management"""
    mcp = MCPServer()

    # Add resources
    mcp.add_resource("config", {"key": "value"})
    mcp.add_resource("api_key", "secret-123")

    # Retrieve resources
    assert mcp.get_resource("config") == {"key": "value"}
    assert mcp.get_resource("api_key") == "secret-123"
    assert mcp.get_resource("nonexistent") is None


def test_mcp_list_tools():
    """Test listing tools"""
    mcp = MCPServer()

    @mcp.tool
    def tool1(x: int) -> int:
        """Tool 1"""
        return x

    @mcp.tool
    def tool2(y: str) -> str:
        """Tool 2"""
        return y

    tools = mcp.list_tools()
    assert len(tools) == 2
    assert tools[0]["name"] == "tool1"
    assert tools[1]["name"] == "tool2"


def test_mcp_to_dict():
    """Test converting MCP server to dictionary"""
    mcp = MCPServer(name="my-server", version="2.0.0")

    @mcp.tool
    def sample_tool() -> str:
        """Sample tool"""
        return "sample"

    mcp.add_resource("res1", "data")

    server_dict = mcp.to_dict()
    assert server_dict["name"] == "my-server"
    assert server_dict["version"] == "2.0.0"
    assert len(server_dict["tools"]) == 1
    assert "res1" in server_dict["resources"]
