"""Example: Planning agent for complex tasks"""

from axm import PlanningAgent

# Create a planning agent
agent = PlanningAgent("gpt-4")

# Add some tools the agent can use
@agent.tool
def search_web(query: str) -> str:
    """Search the web for information"""
    # Simulated search results
    return f"Search results for '{query}': Found relevant information about {query}"


@agent.tool
def save_to_file(content: str, filename: str) -> str:
    """Save content to a file"""
    # Simulated file save
    return f"Saved content to {filename}"


if __name__ == "__main__":
    print("📋 Planning Agent Example\n")

    # Example 1: Simple planning task
    print("Example 1: Research and summarize\n")
    result = agent.execute_plan(
        "Research the top 3 Python web frameworks and create a comparison",
        verbose=True
    )

    print("\n" + "="*60 + "\n")

    # Example 2: More complex task
    print("Example 2: Complex planning\n")
    result = agent.execute_plan(
        "Create a comprehensive guide on machine learning: "
        "1) Research the basics, 2) Identify key algorithms, "
        "3) Find practical applications, 4) Write a summary",
        verbose=True
    )

    print("\n" + "="*60 + "\n")

    # Example 3: Manual plan creation and execution
    print("Example 3: Creating a custom plan\n")

    plan = agent.create_plan("Build a simple web scraper")

    print(f"📋 Created plan for: {plan.goal}\n")
    print(f"Tasks:")
    for i, task in enumerate(plan.tasks, 1):
        deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
        print(f"  {i}. [{task.status}] {task.description}{deps}")
