"""Anthropic Claude LLM provider"""

import json
import os
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Type

from pydantic import BaseModel

try:
    from anthropic import AsyncAnthropic, Anthropic
except ImportError:
    raise ImportError(
        "Anthropic provider requires the anthropic package. "
        "Install it with: pip install axm-agent[anthropic]"
    )

from axm.core.types import Message
from axm.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider

    Reads AXM_ANTHROPIC_API_KEY from environment if api_key not provided.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (default: $AXM_ANTHROPIC_API_KEY)
            base_url: Optional base URL for API
        """
        api_key = api_key or os.environ.get("AXM_ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert internal messages to Anthropic format"""
        result = []
        for msg in messages:
            if msg.role == "system":
                continue  # System messages are handled separately
            elif msg.role == "assistant":
                content = [{"type": "text", "text": msg.content}]
                if msg.tool_calls:
                    # Add tool use blocks
                    for tool_call in msg.tool_calls:
                        content.append(
                            {
                                "type": "tool_use",
                                "id": tool_call["id"],
                                "name": tool_call["function"]["name"],
                                "input": json.loads(tool_call["function"]["arguments"]),
                            }
                        )
                result.append({"role": "assistant", "content": content})
            elif msg.role == "user":
                content = [{"type": "text", "text": msg.content}]
                if msg.tool_call_id:
                    # This is a tool result
                    content = [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.tool_call_id,
                            "content": msg.content,
                        }
                    ]
                result.append({"role": "user", "content": content})
        return result

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type[BaseModel]] = None,
        **kwargs: Any,
    ) -> Message:
        """Generate a response using Anthropic Claude"""
        # Extract system message
        system_content = None
        filtered_messages = []
        for msg in messages:
            if msg.role == "system":
                system_content = msg.content
            else:
                filtered_messages.append(msg)

        anthropic_messages = self._convert_messages(filtered_messages)

        params: Dict[str, Any] = {
            "model": kwargs.get("model", "claude-3-5-sonnet-20241022"),
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4000,
        }

        if system_content:
            params["system"] = system_content

        if tools:
            # Convert tools to Anthropic format
            anthropic_tools = []
            for tool in tools:
                anthropic_tools.append(
                    {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"],
                    }
                )
            params["tools"] = anthropic_tools

        if response_format:
            # Add instruction for JSON output
            schema = response_format.model_json_schema()
            schema_msg = f"\n\nYou must respond with valid JSON matching this schema: {schema}"
            if system_content:
                params["system"] += schema_msg
            else:
                params["system"] = schema_msg.strip()

        response = self.client.messages.create(**params)

        content = ""
        tool_calls = None

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(
                    {
                        "id": block.id,
                        "type": "function",
                        "function": {
                            "name": block.name,
                            "arguments": json.dumps(block.input),
                        },
                    }
                )

        return Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )

    async def agenerate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type[BaseModel]] = None,
        **kwargs: Any,
    ) -> Message:
        """Async generate a response using Anthropic Claude"""
        # Extract system message
        system_content = None
        filtered_messages = []
        for msg in messages:
            if msg.role == "system":
                system_content = msg.content
            else:
                filtered_messages.append(msg)

        anthropic_messages = self._convert_messages(filtered_messages)

        params: Dict[str, Any] = {
            "model": kwargs.get("model", "claude-3-5-sonnet-20241022"),
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4000,
        }

        if system_content:
            params["system"] = system_content

        if tools:
            anthropic_tools = []
            for tool in tools:
                anthropic_tools.append(
                    {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"],
                    }
                )
            params["tools"] = anthropic_tools

        if response_format:
            if system_content:
                params[
                    "system"
                ] += f"\n\nYou must respond with valid JSON matching this schema: {response_format.model_json_schema()}"
            else:
                params["system"] = (
                    f"You must respond with valid JSON matching this schema: {response_format.model_json_schema()}"
                )

        response = await self.async_client.messages.create(**params)

        content = ""
        tool_calls = None

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(
                    {
                        "id": block.id,
                        "type": "function",
                        "function": {
                            "name": block.name,
                            "arguments": json.dumps(block.input),
                        },
                    }
                )

        return Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )

    def stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream response from Anthropic Claude"""
        # Extract system message
        system_content = None
        filtered_messages = []
        for msg in messages:
            if msg.role == "system":
                system_content = msg.content
            else:
                filtered_messages.append(msg)

        anthropic_messages = self._convert_messages(filtered_messages)

        params: Dict[str, Any] = {
            "model": kwargs.get("model", "claude-3-5-sonnet-20241022"),
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4000,
            "stream": True,
        }

        if system_content:
            params["system"] = system_content

        response = self.client.messages.create(**params)

        for chunk in response:
            if chunk.type == "content_block_delta":
                if chunk.delta.type == "text_delta":
                    yield chunk.delta.text

    async def astream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Async stream response from Anthropic Claude"""
        # Extract system message
        system_content = None
        filtered_messages = []
        for msg in messages:
            if msg.role == "system":
                system_content = msg.content
            else:
                filtered_messages.append(msg)

        anthropic_messages = self._convert_messages(filtered_messages)

        params: Dict[str, Any] = {
            "model": kwargs.get("model", "claude-3-5-sonnet-20241022"),
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4000,
            "stream": True,
        }

        if system_content:
            params["system"] = system_content

        response = await self.async_client.messages.create(**params)

        async for chunk in response:
            if chunk.type == "content_block_delta":
                if chunk.delta.type == "text_delta":
                    yield chunk.delta.text
