"""Test script to verify OpenAICompatibleProvider works correctly"""

import os
from axm.core.agent import Agent
from axm.llm.openai_compatible import OpenAICompatibleProvider


def test_openai_compatible_provider_direct():
    """Test that OpenAICompatibleProvider can be instantiated directly"""
    provider = OpenAICompatibleProvider(
        api_key="test-key", base_url="https://custom-endpoint.com/v1"
    )

    print(f"OpenAICompatibleProvider base_url: {provider.base_url}")
    print("Expected: https://custom-endpoint.com/v1")
    assert provider.base_url == "https://custom-endpoint.com/v1"
    assert provider.api_key == "test-key"
    print("✓ OpenAICompatibleProvider direct instantiation test passed")


def test_openai_compatible_provider_env_var():
    """Test that OpenAICompatibleProvider reads from environment variables"""
    provider = OpenAICompatibleProvider()

    # Should read from OPENAI_BASE_URL or default to OpenAI's API
    env_base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    env_api_key = os.environ.get("OPENAI_API_KEY", "")

    print(f"OpenAICompatibleProvider base_url: {provider.base_url}")
    print(f"Expected (from env or default): {env_base_url}")
    assert provider.base_url == env_base_url
    assert provider.api_key == env_api_key
    print("✓ OpenAICompatibleProvider environment variable test passed")


def test_agent_uses_openai_compatible_for_custom_model():
    """Test that Agent uses OpenAICompatibleProvider for non-standard model names"""
    agent = Agent(
        model="custom-model-123",  # Not gpt* or claude*
        api_key="test-key",
        base_url="https://custom-endpoint.com/v1",
    )

    print(f"Agent provider type: {type(agent.llm).__name__}")
    print("Expected: OpenAICompatibleProvider")
    assert isinstance(agent.llm, OpenAICompatibleProvider)
    assert agent.llm.base_url == "https://custom-endpoint.com/v1"
    print("✓ Agent uses OpenAICompatibleProvider for custom model test passed")


def test_openai_compatible_provider_as_model():
    """Test that OpenAICompatibleProvider can be passed as model parameter"""
    provider = OpenAICompatibleProvider(
        api_key="test-key", base_url="https://custom-endpoint.com/v1"
    )
    agent = Agent(model=provider)

    print(f"Agent provider type: {type(agent.llm).__name__}")
    print("Expected: OpenAICompatibleProvider")
    assert isinstance(agent.llm, OpenAICompatibleProvider)
    assert agent.llm.base_url == "https://custom-endpoint.com/v1"
    print("✓ OpenAICompatibleProvider as model parameter test passed")


def test_agent_still_uses_openai_for_gpt():
    """Test that Agent still uses OpenAI provider for gpt models"""
    try:
        from axm.llm.openai import OpenAIProvider

        agent = Agent(model="gpt-4", api_key="test-key")
        print(f"Agent provider type for gpt-4: {type(agent.llm).__name__}")
        print("Expected: OpenAIProvider")
        assert isinstance(agent.llm, OpenAIProvider)
        print("✓ Agent still uses OpenAI for gpt models test passed")
    except ImportError:
        print("⊘ OpenAI test skipped (openai package not installed)")


def test_agent_still_uses_anthropic_for_claude():
    """Test that Agent still uses Anthropic provider for claude models"""
    try:
        from axm.llm.anthropic import AnthropicProvider

        agent = Agent(model="claude-3-5-sonnet-20241022", api_key="test-key")
        print(f"Agent provider type for claude: {type(agent.llm).__name__}")
        print("Expected: AnthropicProvider")
        assert isinstance(agent.llm, AnthropicProvider)
        print("✓ Agent still uses Anthropic for claude models test passed")
    except ImportError:
        print("⊘ Anthropic test skipped (anthropic package not installed)")


if __name__ == "__main__":
    print("Testing OpenAICompatibleProvider implementation...\n")
    test_openai_compatible_provider_direct()
    test_openai_compatible_provider_env_var()
    test_agent_uses_openai_compatible_for_custom_model()
    test_openai_compatible_provider_as_model()
    test_agent_still_uses_openai_for_gpt()
    test_agent_still_uses_anthropic_for_claude()
    print("\n✓ All OpenAICompatibleProvider tests passed!")
