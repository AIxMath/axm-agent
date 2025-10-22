"""OpenAI LLM provider"""

from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Type

from pydantic import BaseModel

try:
    from openai import AsyncOpenAI, OpenAI
except ImportError:
    raise ImportError(
        "OpenAI provider requires the openai package. "
        "Install it with: pip install axm-agent[openai]"
    )

from axm.core.types import Message
from axm.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider (GPT-4, GPT-3.5, etc.)"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert internal messages to OpenAI format"""
        result = []
        for msg in messages:
            openai_msg: Dict[str, Any] = {
                "role": msg.role,
                "content": msg.content,
            }
            if msg.name:
                openai_msg["name"] = msg.name
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id
            result.append(openai_msg)
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
        """Generate a response using OpenAI"""
        openai_messages = self._convert_messages(messages)

        params: Dict[str, Any] = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": openai_messages,
            "temperature": temperature,
        }

        if max_tokens:
            params["max_tokens"] = max_tokens

        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        if response_format:
            # Use JSON mode for structured output
            params["response_format"] = {"type": "json_object"}
            # Add instruction to return JSON
            if openai_messages:
                schema = response_format.model_json_schema()
                openai_messages[-1][
                    "content"
                ] += f"\n\nReturn a JSON object matching this schema: {schema}"

        response = self.client.chat.completions.create(**params)
        choice = response.choices[0]
        message = choice.message

        # Convert back to our Message format
        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]

        return Message(
            role="assistant",
            content=message.content or "",
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
        """Async generate a response using OpenAI"""
        openai_messages = self._convert_messages(messages)

        params: Dict[str, Any] = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": openai_messages,
            "temperature": temperature,
        }

        if max_tokens:
            params["max_tokens"] = max_tokens

        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        if response_format:
            params["response_format"] = {"type": "json_object"}
            if openai_messages:
                openai_messages[-1][
                    "content"
                ] += f"\n\nReturn a JSON object matching this schema: {response_format.model_json_schema()}"

        response = await self.async_client.chat.completions.create(**params)
        choice = response.choices[0]
        message = choice.message

        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]

        return Message(
            role="assistant",
            content=message.content or "",
            tool_calls=tool_calls,
        )

    def stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream response from OpenAI"""
        openai_messages = self._convert_messages(messages)

        params: Dict[str, Any] = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            params["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**params)

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def astream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Async stream response from OpenAI"""
        openai_messages = self._convert_messages(messages)

        params: Dict[str, Any] = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            params["max_tokens"] = max_tokens

        response = await self.async_client.chat.completions.create(**params)

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
