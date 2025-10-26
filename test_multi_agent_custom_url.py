"""Test MultiAgent with custom base_url and api_key"""

import os
from axm.core.agent import Agent
from axm.core.multi_agent import MultiAgent
from axm.llm.openai_compatible import OpenAICompatibleProvider

MODEL = "deepseek-v3-250324"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
API_KEY = os.environ.get("OPENAI_API_KEY", "test-key")


def test_multi_agent_with_custom_url():
    """Test MultiAgent can use custom base_url and api_key"""
    print("\n" + "=" * 60)
    print("TEST: MultiAgent with Custom Base URL")
    print("=" * 60 + "\n")

    # Create agents with custom base_url
    researcher = Agent(
        model=MODEL, role="researcher", base_url=BASE_URL, api_key=API_KEY
    )
    writer = Agent(model=MODEL, role="writer", base_url=BASE_URL, api_key=API_KEY)

    # Verify agents are using OpenAICompatibleProvider
    assert isinstance(researcher.llm, OpenAICompatibleProvider)
    assert isinstance(writer.llm, OpenAICompatibleProvider)
    print(f"✅ Agents created with custom base_url: {BASE_URL}")

    # Create MultiAgent with custom base_url for orchestrator
    team = MultiAgent(
        [researcher, writer],
        orchestrator_model=MODEL,
        base_url=BASE_URL,
        api_key=API_KEY,
    )

    # Verify orchestrator is using OpenAICompatibleProvider
    assert isinstance(team.orchestrator.llm, OpenAICompatibleProvider)
    assert team.orchestrator.llm.base_url == BASE_URL
    print(f"✅ Orchestrator created with custom base_url: {BASE_URL}")

    # Test collaboration
    print("\n🤝 Testing collaboration...")
    result = team.collaborate(
        "Explain quantum computing in one sentence", max_rounds=1, verbose=True
    )

    print("\n" + "=" * 60)
    print("Final Result:")
    print("=" * 60)
    print(result)

    print("\n✅ All tests passed!")


def test_environment_variables():
    """Test that OPENAI_COMPATIBLE_* environment variables work"""
    print("\n" + "=" * 60)
    print("TEST: Environment Variables Priority")
    print("=" * 60 + "\n")

    # Set environment variables
    os.environ["OPENAI_COMPATIBLE_BASE_URL"] = BASE_URL
    os.environ["OPENAI_COMPATIBLE_API_KEY"] = API_KEY

    # Create provider without explicit parameters
    provider = OpenAICompatibleProvider()

    # Verify environment variables were used
    assert provider.base_url == BASE_URL
    assert provider.api_key == API_KEY
    print(f"✅ Provider used OPENAI_COMPATIBLE_BASE_URL: {BASE_URL}")
    print(f"✅ Provider used OPENAI_COMPATIBLE_API_KEY: {API_KEY[:10]}...")

    # Create agent without explicit parameters
    agent = Agent(model=MODEL)
    assert isinstance(agent.llm, OpenAICompatibleProvider)
    assert agent.llm.base_url == BASE_URL
    print(f"✅ Agent used environment variables correctly")

    print("\n✅ All environment variable tests passed!")


if __name__ == "__main__":
    test_multi_agent_with_custom_url()
    test_environment_variables()
