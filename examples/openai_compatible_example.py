"""Example of using OpenAICompatibleProvider with custom endpoints

This provider works with any API that follows the OpenAI chat completions format,
including local LLM servers, custom proxies, or alternative cloud providers.
"""

from axm.core.agent import Agent
from axm.llm.openai_compatible import OpenAICompatibleProvider

# Example 1: Use environment variables (OPENAI_API_KEY and OPENAI_BASE_URL)
# The provider will automatically read these from the environment
print("=== Example 1: Using environment variables ===")
provider_env = OpenAICompatibleProvider()
print(f"Base URL from env: {provider_env.base_url}")
print()

# Example 2: Explicitly set API key and base URL
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

# Example 5: Common use cases
print("=== Example 5: Common use cases ===")

# Local LLM server (e.g., llama.cpp, vLLM, Ollama with OpenAI compatibility)
local_agent = Agent(
    model="llama-3.1-70b",
    api_key="not-needed",  # Local servers often don't need API keys
    base_url="http://localhost:8000/v1",
)

# Alternative cloud provider (e.g., Together AI, Groq, etc.)
cloud_agent = Agent(
    model="mixtral-8x7b-32768",
    api_key="your-api-key",
    base_url="https://api.together.xyz/v1",
)

print("Local agent ready with model: llama-3.1-70b")
print("Cloud agent ready with model: mixtral-8x7b-32768")
print()

print("✓ All examples completed!")
