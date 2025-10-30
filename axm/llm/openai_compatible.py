"""OpenAI-compatible LLM provider using requests library"""

import json
import os
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Type

import requests
from pydantic import BaseModel

try:
    import httpx
except ImportError:
    raise ImportError(
        "OpenAI-compatible provider requires httpx for async support. "
        "Install it with: pip install httpx"
    )

from axm.core.types import Message
from axm.llm.base import LLMProvider


def _strip_markdown_json(content: str) -> str:
    """Strip markdown code blocks from JSON content.

    Some LLMs wrap JSON in markdown ```json ... ``` blocks even when asked not to.
    This helper removes those wrappers.
    """
    content = content.strip()

    # Check if wrapped in markdown code block
    if content.startswith("```"):
        # Find the first newline (end of opening ```)
        first_newline = content.find("\n")
        if first_newline != -1:
            # Find the closing ```
            last_backticks = content.rfind("```")
            if last_backticks > first_newline:
                # Extract content between markers
                content = content[first_newline + 1 : last_backticks].strip()

    return content


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible LLM provider using requests library

    Works with any API that follows the OpenAI chat completions format.
    Reads AXM_OPENAI_COMPATIBLE_API_KEY and AXM_OPENAI_COMPATIBLE_BASE_URL from environment.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize the OpenAI-compatible provider.

        Args:
            api_key: API key for authentication (default: $AXM_OPENAI_COMPATIBLE_API_KEY)
            base_url: Base URL for the API (default: $AXM_OPENAI_COMPATIBLE_BASE_URL)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.environ.get("AXM_OPENAI_COMPATIBLE_API_KEY", "")
        self.base_url = (base_url or os.environ.get("AXM_OPENAI_COMPATIBLE_BASE_URL", "")).rstrip(
            "/"
        )

        self.timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

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
        """Generate a response using the OpenAI-compatible provider"""
        openai_messages = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": openai_messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        if response_format:
            # Use JSON mode for structured output
            payload["response_format"] = {"type": "json_object"}
            # Add instruction to return JSON
            if openai_messages:
                schema = response_format.model_json_schema()
                openai_messages[-1][
                    "content"
                ] += f"\n\nReturn a JSON object matching this schema: {schema}\nDirectly reply json content. NEVER wrap it with markdown formats."

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            print(e)
            raise ConnectionError(
                f"Failed to connect to {self.base_url}. "
                f"Please check:\n"
                f"  1. The base_url is correct\n"
                f"  2. You have internet connectivity\n"
                f"  3. The API endpoint is accessible from your network\n"
                f"Original error: {e}"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Timeout in {self.__class__.__name__}: Request to {self.base_url} timed out after {self.timeout}s")
        except requests.exceptions.HTTPError as e:
            raise Exception(
                f"HTTP error in {self.__class__.__name__}: HTTP error from {self.base_url}: {e.response.status_code} - {e.response.text}"
            )

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        # Convert back to our Message format
        tool_calls = None
        if message.get("tool_calls"):
            tool_calls = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"],
                    },
                }
                for tc in message["tool_calls"]
            ]

        # Clean content - remove markdown wrappers if present (common with structured output)
        content = message.get("content") or ""
        if response_format and content:
            content = _strip_markdown_json(content)

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
        """Async generate a response using the OpenAI-compatible provider"""
        openai_messages = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": openai_messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        if response_format:
            payload["response_format"] = {"type": "json_object"}
            if openai_messages:
                openai_messages[-1][
                    "content"
                ] += f"\n\nReturn a JSON object matching this schema: {response_format.model_json_schema()}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to {self.base_url}. "
                f"Please check:\n"
                f"  1. The base_url is correct\n"
                f"  2. You have internet connectivity\n"
                f"  3. The API endpoint is accessible from your network\n"
                f"Original error: {e}"
            )
        except httpx.TimeoutException:
            raise TimeoutError(f"Request to {self.base_url} timed out after {self.timeout}s")
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"HTTP error from {self.base_url}: {e.response.status_code} - {e.response.text}"
            )

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        tool_calls = None
        if message.get("tool_calls"):
            tool_calls = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"],
                    },
                }
                for tc in message["tool_calls"]
            ]

        # Clean content - remove markdown wrappers if present (common with structured output)
        content = message.get("content") or ""
        if response_format and content:
            content = _strip_markdown_json(content)

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
        """Stream response from the OpenAI-compatible provider"""
        openai_messages = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._get_headers(),
            json=payload,
            timeout=self.timeout,
            stream=True,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode("utf-8")
            if line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix
                if data_str.strip() == "[DONE]":
                    break

                try:
                    chunk_data = json.loads(data_str)
                    delta = chunk_data["choices"][0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        yield delta["content"]
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

    async def astream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Async stream response from the OpenAI-compatible provider"""
        openai_messages = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str.strip() == "[DONE]":
                            break

                        try:
                            chunk_data = json.loads(data_str)
                            delta = chunk_data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
