"""Test script to verify base_url parameter works correctly"""

from axm.core.agent import Agent


def test_openai_base_url():
    """Test that base_url is passed to OpenAI provider"""
    agent = Agent(
        model="gpt-4",
        api_key="test-key",
        base_url="https://custom-openai-endpoint.com/v1"
    )

    print(f"OpenAI base_url: {agent.llm.client.base_url}")
    print(f"Expected: https://custom-openai-endpoint.com/v1")
    # The base_url is stored as a URL object, so we convert to string
    assert str(agent.llm.client.base_url) == "https://custom-openai-endpoint.com/v1/"
    print("✓ OpenAI base_url test passed")


def test_anthropic_base_url():
    """Test that base_url is passed to Anthropic provider"""
    try:
        agent = Agent(
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
            base_url="https://custom-anthropic-endpoint.com"
        )

        print(f"Anthropic base_url: {agent.llm.client.base_url}")
        print(f"Expected: https://custom-anthropic-endpoint.com")
        # The base_url is stored as a URL object, so we convert to string
        assert str(agent.llm.client.base_url) == "https://custom-anthropic-endpoint.com/"
        print("✓ Anthropic base_url test passed")
    except ImportError:
        print("⊘ Anthropic test skipped (anthropic package not installed)")


def test_default_base_url():
    """Test that agents work without base_url (use default)"""
    # This should not raise an error
    agent_openai = Agent(model="gpt-4", api_key="test-key")

    try:
        agent_claude = Agent(model="claude-3-5-sonnet-20241022", api_key="test-key")
    except ImportError:
        pass  # Skip if anthropic not installed

    print("✓ Default base_url test passed")


if __name__ == "__main__":
    test_openai_base_url()
    test_anthropic_base_url()
    test_default_base_url()
    print("\n✓ All tests passed!")
