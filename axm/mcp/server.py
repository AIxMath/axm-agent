"""Model Context Protocol (MCP) server implementation"""

from typing import Any, Callable, Dict, List, Optional

from axm.core.decorators import tool as tool_decorator
from axm.tools.base import FunctionTool, Tool


class MCPServer:
    """
    Model Context Protocol server for managing tools.

    MCP is a protocol for exposing tools and resources to AI agents.

    Example:
        mcp = MCPServer()

        @mcp.tool
        def search(query: str) -> list:
            return ["result1", "result2"]

        agent = Agent("gpt-4", mcp_server=mcp)
    """

    def __init__(self, name: str = "mcp-server", version: str = "0.1.0"):
        """
        Initialize an MCP server.

        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self.tools: Dict[str, Tool] = {}
        self.resources: Dict[str, Any] = {}

    def tool(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Callable:
        """
        Decorator to register a function as an MCP tool.

        Example:
            @mcp.tool
            def get_time() -> str:
                return datetime.now().isoformat()
        """

        def decorator(f: Callable) -> Callable:
            decorated_func = tool_decorator(f, name=name, description=description)

            tool_name = decorated_func._tool_name
            tool_description = decorated_func._tool_description
            tool_model = decorated_func._tool_model

            # Create parameters schema
            schema = tool_model.model_json_schema()
            parameters_schema = {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", []),
            }

            # Register the tool
            function_tool = FunctionTool(
                name=tool_name,
                description=tool_description,
                function=f,
                parameters_schema=parameters_schema,
            )
            self.tools[tool_name] = function_tool

            return decorated_func

        if func is None:
            return decorator
        else:
            return decorator(func)

    def add_tool(self, tool: Tool) -> None:
        """Add a tool to the server"""
        self.tools[tool.name] = tool

    def get_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)

    def execute_tool(self, name: str, **kwargs: Any) -> Any:
        """Execute a tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")

        return self.tools[name].execute(**kwargs)

    def add_resource(self, name: str, resource: Any) -> None:
        """
        Add a resource to the server.

        Resources can be data, configurations, or any other objects
        that tools might need access to.
        """
        self.resources[name] = resource

    def get_resource(self, name: str) -> Any:
        """Get a resource by name"""
        return self.resources.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools with their metadata"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool._get_parameters(),
            }
            for tool in self.tools.values()
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert server to dictionary representation"""
        return {
            "name": self.name,
            "version": self.version,
            "tools": self.list_tools(),
            "resources": list(self.resources.keys()),
        }
