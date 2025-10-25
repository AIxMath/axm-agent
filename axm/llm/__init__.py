"""LLM providers"""

from axm.llm.base import LLMProvider

# Lazy imports for providers - only import when used
__all__ = ["LLMProvider", "OpenAIProvider", "AnthropicProvider", "OpenAICompatibleProvider"]


def __getattr__(name):
    """Lazy import providers to avoid requiring optional dependencies"""
    if name == "OpenAIProvider":
        from axm.llm.openai import OpenAIProvider

        return OpenAIProvider
    elif name == "AnthropicProvider":
        from axm.llm.anthropic import AnthropicProvider

        return AnthropicProvider
    elif name == "OpenAICompatibleProvider":
        from axm.llm.openai_compatible import OpenAICompatibleProvider

        return OpenAICompatibleProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
