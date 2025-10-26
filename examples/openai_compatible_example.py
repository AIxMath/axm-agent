"""Example of using OpenAICompatibleProvider with custom endpoints

This provider works with any API that follows the OpenAI chat completions format,
including local LLM servers, custom proxies, or alternative cloud providers.

Environment Variables:
- AXM_OPENAI_COMPATIBLE_API_KEY: API key for authentication
- AXM_OPENAI_COMPATIBLE_BASE_URL: Base URL for the API endpoint

Examples:
  export AXM_OPENAI_COMPATIBLE_BASE_URL="https://your-endpoint.com/v1"
  export AXM_OPENAI_COMPATIBLE_API_KEY="your-api-key"
"""

from axm.core.agent import Agent
from axm.core.multi_agent import MultiAgent
from axm.llm.openai_compatible import OpenAICompatibleProvider

# Example 1: Use environment variables (RECOMMENDED)
# Set these in your shell or .env file:
# export AXM_OPENAI_COMPATIBLE_BASE_URL="https://your-endpoint.com/v1"
# export AXM_OPENAI_COMPATIBLE_API_KEY="your-api-key"
print("=== Example 1: Using environment variables ===")
provider_env = OpenAICompatibleProvider()
print(f"Base URL from env: {provider_env.base_url}")
print()

# Example 2: Explicitly set API key and base URL (overrides environment)
print("=== Example 2: Explicit configuration ===")
provider = OpenAICompatibleProvider(
    api_key="your-api-key",
    base_url="https://your-custom-endpoint.com/v1",
    timeout=30,  # Optional: custom timeout in seconds
)
print(f"Base URL: {provider.base_url}")
print()

# Example 3: Use with Agent - custom model name
print("=== Example 3: Agent with custom model ===")
agent = Agent(
    model="custom-llm-v1",  # Any non-gpt/non-claude model uses OpenAICompatibleProvider
    api_key="your-api-key",
    base_url="https://your-custom-endpoint.com/v1",
)
print(f"Provider type: {type(agent.llm).__name__}")
print()

# Example 4: Pass provider directly to Agent
print("=== Example 4: Pass provider to Agent ===")
custom_provider = OpenAICompatibleProvider(
    api_key="your-api-key", base_url="https://your-endpoint.com/v1"
)
agent = Agent(model=custom_provider)
print(f"Provider type: {type(agent.llm).__name__}")
print()

# Example 5: MultiAgent with custom endpoint
print("=== Example 5: MultiAgent with custom endpoint ===")
researcher = Agent(
    model="deepseek-v3",
    role="researcher",
    api_key="your-api-key",
    base_url="https://your-endpoint.com/v1",
)
writer = Agent(
    model="deepseek-v3",
    role="writer",
    api_key="your-api-key",
    base_url="https://your-endpoint.com/v1",
)

# IMPORTANT: Pass api_key and base_url to MultiAgent for the orchestrator
team = MultiAgent(
    [researcher, writer],
    orchestrator_model="deepseek-v3",
    api_key="your-api-key",
    base_url="https://your-endpoint.com/v1",
)
print(f"Orchestrator provider: {type(team.orchestrator.llm).__name__}")
print()

# Example 6: Common use cases
print("=== Example 6: Common use cases ===")

# Local LLM server (e.g., llama.cpp, vLLM, Ollama with OpenAI compatibility)
local_agent = Agent(
    model="llama-3.1-70b",
    api_key="not-needed",  # Local servers often don't need API keys
    base_url="http://localhost:8000/v1",
)

# Alternative cloud provider (e.g., Together AI, Groq, DeepSeek, etc.)
cloud_agent = Agent(
    model="mixtral-8x7b-32768",
    api_key="your-api-key",
    base_url="https://api.together.xyz/v1",
)

print("Local agent ready with model: llama-3.1-70b")
print("Cloud agent ready with model: mixtral-8x7b-32768")
print()

print("✓ All examples completed!")
