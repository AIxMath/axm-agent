"""Example: Multi-agent collaboration"""

from axm import Agent, MultiAgent

# Create specialized agents
researcher = Agent(
    "gpt-4",
    role="researcher",
    system_prompt="You are a researcher. Focus on gathering facts, data, and information."
)

writer = Agent(
    "gpt-4",
    role="writer",
    system_prompt="You are a creative writer. Focus on clear, engaging writing."
)

critic = Agent(
    "gpt-4",
    role="critic",
    system_prompt="You are a critic. Provide constructive feedback to improve quality."
)

# Create multi-agent system
team = MultiAgent([researcher, writer, critic])

if __name__ == "__main__":
    print("🤝 Multi-Agent Collaboration Example\n")

    # Example 1: Collaborate on article writing
    print("Task: Write an article about the benefits of AI agents\n")

    result = team.collaborate(
        "Write a 3-paragraph article about the benefits of AI agents in software development",
        max_rounds=3,
        verbose=True
    )

    print("\n" + "="*60 + "\n")
    print("📄 Final Article:\n")
    print(result)

    print("\n" + "="*60 + "\n")

    # Example 2: Different task
    print("\nTask: Create a product description\n")

    result = team.collaborate(
        "Create a compelling product description for a new AI-powered task manager app",
        max_rounds=2,
        verbose=True
    )

    print("\n" + "="*60 + "\n")
    print("📄 Final Product Description:\n")
    print(result)
