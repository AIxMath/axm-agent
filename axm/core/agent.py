"""Core Agent implementation"""

import json
from typing import Any, AsyncIterator, Callable, Dict, Iterator, List, Optional, Type, Union

from pydantic import BaseModel

from axm.core.types import AgentConfig, Message
from axm.core.decorators import tool as tool_decorator
from axm.llm.base import LLMProvider
from axm.memory.conversation import ConversationMemory
from axm.tools.base import FunctionTool, Tool


class Agent:
    """
    Main Agent class for building AI agents with tools and memory.

    Example:
        agent = Agent("gpt-4")

        @agent.tool
        def get_weather(city: str) -> str:
            return f"Sunny in {city}"

        response = agent.run("What's the weather in Paris?")
    """

    def __init__(
        self,
        model: Union[str, LLMProvider] = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        timeout: int = 60,
        system_prompt: Optional[str] = None,
        role: Optional[str] = None,
        memory: Optional[ConversationMemory] = None,
        mcp_server: Optional[Any] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize an Agent.

        Args:
            model: Model name or LLMProvider instance
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
            max_retries: Maximum retry attempts on failure
            timeout: Timeout in seconds
            system_prompt: System prompt for the agent
            role: Role description for multi-agent systems
            memory: Conversation memory instance
            mcp_server: MCP server for tool integration
            api_key: API key for the LLM provider
            base_url: Base URL for the LLM provider API
        """
        self.config = AgentConfig(
            model=model if isinstance(model, str) else "custom",
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            timeout=timeout,
            system_prompt=system_prompt,
            role=role,
        )

        # Initialize LLM provider
        if isinstance(model, LLMProvider):
            self.llm = model
        elif isinstance(model, str):
            # Auto-detect provider based on model name
            if model.startswith("gpt") or model.startswith("o1"):
                from axm.llm.openai import OpenAIProvider

                self.llm = OpenAIProvider(api_key=api_key, base_url=base_url)
            elif model.startswith("claude"):
                from axm.llm.anthropic import AnthropicProvider

                self.llm = AnthropicProvider(api_key=api_key, base_url=base_url)
            else:
                # Default to OpenAI-compatible provider (uses requests library)
                from axm.llm.openai_compatible import OpenAICompatibleProvider

                self.llm = OpenAICompatibleProvider(api_key=api_key, base_url=base_url)
        else:
            raise ValueError("model must be a string or LLMProvider instance")

        self.memory = memory or ConversationMemory()
        self.tools: Dict[str, Tool] = {}
        self.mcp_server = mcp_server

        # Add system prompt if provided
        if system_prompt:
            self.memory.add_message(Message(role="system", content=system_prompt))
        elif role:
            self.memory.add_message(
                Message(role="system", content=f"You are a {role}. Respond accordingly.")
            )

        # Load tools from MCP server if provided
        if mcp_server:
            self._load_mcp_tools()

    def _load_mcp_tools(self) -> None:
        """Load tools from MCP server"""
        if self.mcp_server and hasattr(self.mcp_server, "get_tools"):
            for tool in self.mcp_server.get_tools():
                self.tools[tool.name] = tool

    def tool(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Callable:
        """
        Decorator to register a function as a tool.

        Example:
            @agent.tool
            def search(query: str) -> str:
                return f"Results for {query}"
        """

        def decorator(f: Callable) -> Callable:
            # Apply the tool decorator
            decorated_func = tool_decorator(f, name=name, description=description)

            # Extract tool metadata
            tool_name = decorated_func._tool_name
            tool_description = decorated_func._tool_description
            tool_model = decorated_func._tool_model

            # Create parameters schema from Pydantic model
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

    def add_tool(self, tool: Union[Tool, Callable]) -> None:
        """Add a tool to the agent"""
        if isinstance(tool, Tool):
            self.tools[tool.name] = tool
        elif callable(tool):
            # Convert function to tool
            self.tool(tool)
        else:
            raise ValueError("Tool must be a Tool instance or callable")

    def run(
        self,
        prompt: str,
        response_format: Optional[Type[BaseModel]] = None,
        max_iterations: int = 10,
    ) -> Union[str, BaseModel]:
        """
        Run the agent with a user prompt.

        Args:
            prompt: User input prompt
            response_format: Optional Pydantic model for structured output
            max_iterations: Maximum tool-calling iterations

        Returns:
            Response string or Pydantic model instance
        """
        # Add user message to memory
        self.memory.add_message(Message(role="user", content=prompt))

        iteration = 0
        while iteration < max_iterations:
            iteration += 1

            # Prepare tools for LLM
            tools_list = None
            if self.tools:
                tools_list = [tool.to_dict() for tool in self.tools.values()]

            # Generate response
            response = self.llm.generate(
                messages=self.memory.messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=tools_list,
                response_format=response_format,
                model=self.config.model,
                timeout=self.config.timeout,
            )

            # Add assistant response to memory
            self.memory.add_message(response)

            # Check if we need to execute tools
            if response.tool_calls:
                # Execute all tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])

                    if tool_name in self.tools:
                        try:
                            result = self.tools[tool_name].execute(**tool_args)
                            result_str = str(result)
                        except Exception as e:
                            result_str = f"Error executing tool: {str(e)}"

                        # Add tool result to memory
                        self.memory.add_message(
                            Message(
                                role="tool",
                                content=result_str,
                                tool_call_id=tool_call["id"],
                                name=tool_name,
                            )
                        )
                    else:
                        self.memory.add_message(
                            Message(
                                role="tool",
                                content=f"Tool {tool_name} not found",
                                tool_call_id=tool_call["id"],
                                name=tool_name,
                            )
                        )
                # Continue loop to get final response
                continue
            else:
                # No tool calls, we have the final response
                if response_format:
                    # Parse JSON response into Pydantic model
                    try:
                        json_data = json.loads(response.content)
                        return response_format(**json_data)
                    except (json.JSONDecodeError, ValueError) as e:
                        raise ValueError(
                            f"Failed to parse response as {response_format.__name__}: {e}"
                        )
                else:
                    return response.content

        raise RuntimeError(f"Max iterations ({max_iterations}) reached without completion")

    async def arun(
        self,
        prompt: str,
        response_format: Optional[Type[BaseModel]] = None,
        max_iterations: int = 10,
    ) -> Union[str, BaseModel]:
        """Async version of run()"""
        self.memory.add_message(Message(role="user", content=prompt))

        iteration = 0
        while iteration < max_iterations:
            iteration += 1

            tools_list = None
            if self.tools:
                tools_list = [tool.to_dict() for tool in self.tools.values()]

            response = await self.llm.agenerate(
                messages=self.memory.messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=tools_list,
                response_format=response_format,
                model=self.config.model,
                timeout=self.config.timeout,
            )

            self.memory.add_message(response)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])

                    if tool_name in self.tools:
                        try:
                            result = self.tools[tool_name].execute(**tool_args)
                            result_str = str(result)
                        except Exception as e:
                            result_str = f"Error executing tool: {str(e)}"

                        self.memory.add_message(
                            Message(
                                role="tool",
                                content=result_str,
                                tool_call_id=tool_call["id"],
                                name=tool_name,
                            )
                        )
                    else:
                        self.memory.add_message(
                            Message(
                                role="tool",
                                content=f"Tool {tool_name} not found",
                                tool_call_id=tool_call["id"],
                                name=tool_name,
                            )
                        )
                continue
            else:
                if response_format:
                    try:
                        json_data = json.loads(response.content)
                        return response_format(**json_data)
                    except (json.JSONDecodeError, ValueError) as e:
                        raise ValueError(
                            f"Failed to parse response as {response_format.__name__}: {e}"
                        )
                else:
                    return response.content

        raise RuntimeError(f"Max iterations ({max_iterations}) reached without completion")

    def stream(self, prompt: str) -> Iterator[str]:
        """Stream the agent's response"""
        self.memory.add_message(Message(role="user", content=prompt))

        for chunk in self.llm.stream(
            messages=self.memory.messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            model=self.config.model,
            timeout=self.config.timeout,
        ):
            yield chunk

    async def astream(self, prompt: str) -> AsyncIterator[str]:
        """Async stream the agent's response"""
        self.memory.add_message(Message(role="user", content=prompt))

        async for chunk in self.llm.astream(
            messages=self.memory.messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            model=self.config.model,
            timeout=self.config.timeout,
        ):
            yield chunk

    def reset(self) -> None:
        """Reset the agent's conversation memory"""
        system_messages = [msg for msg in self.memory.messages if msg.role == "system"]
        self.memory.messages.clear()
        self.memory.messages.extend(system_messages)

    def get_history(self) -> List[Message]:
        """Get the conversation history"""
        return self.memory.messages.copy()
