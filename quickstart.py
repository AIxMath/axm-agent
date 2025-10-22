"""
Quick Start Script - Get up and running with AXM Agent in seconds!

Run this script to see AXM Agent in action.
Make sure to set your OPENAI_API_KEY environment variable first.
"""

import os
from axm import Agent, PlanningAgent, MultiAgent

def demo_basic_agent():
    """Demo 1: Basic agent usage"""
    print("\n" + "="*60)
    print("DEMO 1: Basic Agent")
    print("="*60 + "\n")

    agent = Agent("gpt-4")

    # Simple conversation
    response = agent.run("What is 5 + 3?")
    print(f"Q: What is 5 + 3?")
    print(f"A: {response}\n")


def demo_agent_with_tools():
    """Demo 2: Agent with custom tools"""
    print("\n" + "="*60)
    print("DEMO 2: Agent with Custom Tools")
    print("="*60 + "\n")

    agent = Agent("gpt-4")

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
    print(f"Request: Get info for user 1 and send email")
    print(f"Response: {response}\n")


def demo_structured_output():
    """Demo 3: Structured output with Pydantic"""
    print("\n" + "="*60)
    print("DEMO 3: Structured Output")
    print("="*60 + "\n")

    from pydantic import BaseModel

    class MovieRecommendation(BaseModel):
        title: str
        year: int
        genre: str
        rating: float
        why_recommended: str

    agent = Agent("gpt-4")
    movie = agent.run(
        "Recommend a sci-fi movie for someone who loves AI themes",
        response_format=MovieRecommendation
    )

    print("Movie Recommendation:")
    print(f"  Title: {movie.title} ({movie.year})")
    print(f"  Genre: {movie.genre}")
    print(f"  Rating: {movie.rating}/10")
    print(f"  Why: {movie.why_recommended}\n")


def demo_planning_agent():
    """Demo 4: Planning agent"""
    print("\n" + "="*60)
    print("DEMO 4: Planning Agent")
    print("="*60 + "\n")

    agent = PlanningAgent("gpt-4")

    result = agent.execute_plan(
        "Research the benefits of Python for data science and create a summary",
        verbose=True
    )


def demo_multi_agent():
    """Demo 5: Multi-agent collaboration"""
    print("\n" + "="*60)
    print("DEMO 5: Multi-Agent Collaboration")
    print("="*60 + "\n")

    researcher = Agent("gpt-4", role="researcher")
    writer = Agent("gpt-4", role="writer")

    team = MultiAgent([researcher, writer])

    result = team.collaborate(
        "Create a brief explanation of quantum computing for beginners",
        max_rounds=2,
        verbose=True
    )

    print("\n" + "="*60)
    print("Final Result:")
    print("="*60)
    print(result)


def main():
    """Run all demos"""
    print("\n" + "🤖 "*20)
    print("Welcome to AXM Agent Quick Start!")
    print("🤖 "*20)

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: OPENAI_API_KEY not set!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nContinuing with demos (they may fail without a valid key)...\n")

    try:
        # Run demos
        demo_basic_agent()
        demo_agent_with_tools()
        demo_structured_output()
        demo_planning_agent()
        demo_multi_agent()

        print("\n" + "="*60)
        print("✅ Quick start complete!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Check out the examples/ directory for more examples")
        print("  2. Read the docs/ directory for detailed documentation")
        print("  3. Start building your own agents!")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Set your OPENAI_API_KEY")
        print("  2. Installed axm-agent with: pip install axm-agent[openai]")
        print("  3. Have internet connectivity")


if __name__ == "__main__":
    main()
