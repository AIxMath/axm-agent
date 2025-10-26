"""
Quick Start Script - Get up and running with AXM Agent in seconds!

Run this script to see AXM Agent in action.
Set your OPENAI_COMPATIBLE_BASE_URL and OPENAI_COMPATIBLE_API_KEY environment variables.
Or use OPENAI_BASE_URL and OPENAI_API_KEY as fallback.
"""

import os
from axm.core.agent import Agent
from axm.core.planning_agent import PlanningAgent
from axm.core.multi_agent import MultiAgent
from axm.llm.openai_compatible import OpenAICompatibleProvider

MODEL = "deepseek-v3-250324"
# Note: The base_url should end with /v1 (or similar version endpoint)
# not include /chat/completions - that's added automatically by the provider
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
API_KEY = os.environ.get("OPENAI_API_KEY", "test-key-please-set-env-var")


def demo_basic_agent():
    """Demo 1: Basic agent usage"""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Agent")
    print("=" * 60 + "\n")

    agent = Agent(model=MODEL, base_url=BASE_URL, api_key=API_KEY)

    assert isinstance(agent.llm, OpenAICompatibleProvider)

    # Simple conversation
    response = agent.run("What is 5 + 3?")
    print("Q: What is 5 + 3?")
    print(f"A: {response}\n")


def demo_agent_with_tools():
    """Demo 2: Agent with custom tools"""
    print("\n" + "=" * 60)
    print("DEMO 2: Agent with Custom Tools")
    print("=" * 60 + "\n")

    agent = Agent(model=MODEL, base_url=BASE_URL, api_key=API_KEY)

    @agent.tool
    def get_user_info(user_id: int) -> dict:
        """Get user information by ID"""
        # Simulated database
        users = {
            1: {"name": "Alice", "age": 30, "city": "New York"},
            2: {"name": "Bob", "age": 25, "city": "San Francisco"},
        }
        return users.get(user_id, {"error": "User not found"})

    @agent.tool
    def send_email(to: str, subject: str) -> str:
        """Send an email"""
        return f"Email sent to {to} with subject: {subject}"

    response = agent.run("Get information for user ID 1 and send them an email about their account")
    print("Request: Get info for user 1 and send email")
    print(f"Response: {response}\n")


def demo_structured_output():
    """Demo 3: Structured output with Pydantic"""
    print("\n" + "=" * 60)
    print("DEMO 3: Structured Output")
    print("=" * 60 + "\n")

    from pydantic import BaseModel

    class MovieRecommendation(BaseModel):
        title: str
        year: int
        genre: str
        rating: float
        why_recommended: str

    agent = Agent(model=MODEL, base_url=BASE_URL, api_key=API_KEY)
    movie = agent.run(
        "Recommend a sci-fi movie for someone who loves AI themes",
        response_format=MovieRecommendation,
    )

    print("Movie Recommendation:")
    print(f"  Title: {movie.title} ({movie.year})")
    print(f"  Genre: {movie.genre}")
    print(f"  Rating: {movie.rating}/10")
    print(f"  Why: {movie.why_recommended}\n")


def demo_planning_agent():
    """Demo 4: Planning agent"""
    print("\n" + "=" * 60)
    print("DEMO 4: Planning Agent")
    print("=" * 60 + "\n")

    agent = PlanningAgent(model=MODEL, base_url=BASE_URL, api_key=API_KEY)

    agent.execute_plan(
        "Research the benefits of Python for data science and create a summary",
        verbose=True,
    )


def demo_multi_agent():
    """Demo 5: Multi-agent collaboration"""
    print("\n" + "=" * 60)
    print("DEMO 5: Multi-Agent Collaboration")
    print("=" * 60 + "\n")

    researcher = Agent(model=MODEL, role="researcher", base_url=BASE_URL, api_key=API_KEY)
    writer = Agent(model=MODEL, role="writer", base_url=BASE_URL, api_key=API_KEY)

    team = MultiAgent(
        [researcher, writer],
        orchestrator_model=MODEL,
        base_url=BASE_URL,
        api_key=API_KEY,
    )

    result = team.collaborate(
        "Create a brief explanation of quantum computing for beginners", max_rounds=2, verbose=True
    )

    print("\n" + "=" * 60)
    print("Final Result:")
    print("=" * 60)
    print(result)


def main():
    """Run all demos"""
    print("\n" + "🤖 " * 20)
    print("Welcome to AXM Agent Quick Start!")
    print("🤖 " * 20)

    try:
        # Run demos
        demo_basic_agent()
        demo_agent_with_tools()
        demo_structured_output()
        demo_planning_agent()
        demo_multi_agent()

        print("\n" + "=" * 60)
        print("✅ Quick start complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Check out the examples/ directory for more examples")
        print("  2. Read the docs/ directory for detailed documentation")
        print("  3. Start building your own agents!")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if the BASE_URL endpoint is accessible from your network")
        print("  2. Set your API key via OPENAI_API_KEY environment variable")
        print("  3. Ensure you have internet connectivity")
        print("  4. For custom endpoints (like Volcano Engine), ensure:")
        print("     - You're on the correct network (VPN if needed)")
        print("     - The endpoint URL is correct")
        print("     - Your API key is valid")
        print("\nTo test with a local endpoint, try:")
        print("  BASE_URL='http://localhost:8000/v1'")
        print("  Or use a public endpoint like OpenAI's API")


if __name__ == "__main__":
    main()
