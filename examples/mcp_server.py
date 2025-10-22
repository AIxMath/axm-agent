"""Example: MCP server integration"""

from axm import Agent, MCPServer
import datetime

# Create an MCP server
mcp = MCPServer(name="my-tools", version="1.0.0")


# Register tools with the MCP server
@mcp.tool
def get_current_time() -> str:
    """Get the current time"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool
def reverse_string(text: str) -> str:
    """Reverse a string"""
    return text[::-1]


@mcp.tool
def count_words(text: str) -> int:
    """Count words in a text"""
    return len(text.split())


@mcp.tool
def to_uppercase(text: str) -> str:
    """Convert text to uppercase"""
    return text.upper()


# Add a resource to the MCP server
mcp.add_resource("api_key", "secret-key-12345")
mcp.add_resource("config", {"max_retries": 3, "timeout": 30})

# Create an agent with the MCP server
agent = Agent("gpt-4", mcp_server=mcp)

if __name__ == "__main__":
    print("🔌 MCP Server Example\n")

    # List available tools
    print("Available tools on MCP server:")
    for tool_info in mcp.list_tools():
        print(f"  - {tool_info['name']}: {tool_info['description']}")
    print()

    # Use the agent with MCP tools
    print("="*60)
    print("\nExample 1: Using time tool\n")
    response = agent.run("What time is it right now?")
    print(f"User: What time is it right now?")
    print(f"Agent: {response}\n")

    print("="*60)
    print("\nExample 2: Using string manipulation tools\n")
    response = agent.run("Reverse the string 'Hello World' and convert it to uppercase")
    print(f"User: Reverse the string 'Hello World' and convert it to uppercase")
    print(f"Agent: {response}\n")

    print("="*60)
    print("\nExample 3: Count words\n")
    response = agent.run("How many words are in this sentence: 'The quick brown fox jumps over the lazy dog'")
    print(f"User: How many words are in this sentence: 'The quick brown fox jumps over the lazy dog'")
    print(f"Agent: {response}\n")

    print("="*60)
    print("\nMCP Server Information:")
    server_info = mcp.to_dict()
    print(f"Name: {server_info['name']}")
    print(f"Version: {server_info['version']}")
    print(f"Tools: {len(server_info['tools'])}")
    print(f"Resources: {server_info['resources']}")
