"""Example: Basic agent with tools"""

from axm import Agent

# Create an agent
agent = Agent("gpt-4")


# Define tools using decorator
@agent.tool
def get_weather(city: str) -> str:
    """Get the current weather for a city"""
    # In a real app, this would call a weather API
    return f"The weather in {city} is sunny and 72°F"


@agent.tool
def calculate(expression: str) -> float:
    """Safely evaluate a mathematical expression"""
    # Simple calculator (in production, use a proper parser)
    try:
        # Only allow numbers and basic operators
        allowed_chars = "0123456789+-*/(). "
        if all(c in allowed_chars for c in expression):
            return eval(expression, {"__builtins__": {}})
        else:
            return "Invalid expression"
    except Exception as e:
        return f"Error: {str(e)}"


# Use the agent
if __name__ == "__main__":
    print("🤖 Agent with Tools Example\n")

    # Example 1: Using weather tool
    response = agent.run("What's the weather like in Paris?")
    print("User: What's the weather like in Paris?")
    print(f"Agent: {response}\n")

    # Example 2: Using calculator tool
    response = agent.run("What is 25 * 4 + 10?")
    print("User: What is 25 * 4 + 10?")
    print(f"Agent: {response}\n")

    # Example 3: Multiple tools in one query
    response = agent.run("What's the weather in Tokyo and what is 100 / 5?")
    print("User: What's the weather in Tokyo and what is 100 / 5?")
    print(f"Agent: {response}")
