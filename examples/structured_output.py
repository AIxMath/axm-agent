"""Example: Structured output with Pydantic"""

from axm import Agent
from pydantic import BaseModel, Field
from typing import List


# Define output schema
class Recipe(BaseModel):
    name: str = Field(description="Name of the recipe")
    ingredients: List[str] = Field(description="List of ingredients")
    instructions: List[str] = Field(description="Step-by-step instructions")
    prep_time: int = Field(description="Preparation time in minutes")
    difficulty: str = Field(description="Difficulty level: easy, medium, or hard")


class WeatherReport(BaseModel):
    city: str
    temperature: float = Field(description="Temperature in Fahrenheit")
    conditions: str = Field(description="Weather conditions")
    humidity: int = Field(description="Humidity percentage")
    wind_speed: float = Field(description="Wind speed in mph")


# Create agent
agent = Agent("gpt-4")

if __name__ == "__main__":
    print("📊 Structured Output Example\n")

    # Example 1: Generate a recipe
    print("1. Generating a recipe for chocolate chip cookies...\n")
    recipe = agent.run("Generate a recipe for chocolate chip cookies", response_format=Recipe)

    print(f"Recipe: {recipe.name}")
    print(f"Difficulty: {recipe.difficulty}")
    print(f"Prep time: {recipe.prep_time} minutes")
    print("\nIngredients:")
    for ingredient in recipe.ingredients:
        print(f"  - {ingredient}")
    print("\nInstructions:")
    for i, instruction in enumerate(recipe.instructions, 1):
        print(f"  {i}. {instruction}")

    print("\n" + "=" * 50 + "\n")

    # Example 2: Generate a weather report
    print("2. Generating a weather report for San Francisco...\n")
    weather = agent.run(
        "Generate a realistic weather report for San Francisco in summer",
        response_format=WeatherReport,
    )

    print(f"Weather Report for {weather.city}")
    print(f"Temperature: {weather.temperature}°F")
    print(f"Conditions: {weather.conditions}")
    print(f"Humidity: {weather.humidity}%")
    print(f"Wind Speed: {weather.wind_speed} mph")
