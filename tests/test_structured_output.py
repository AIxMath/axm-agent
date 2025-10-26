"""Test structured output with markdown stripping"""

import os
from pydantic import BaseModel
from axm.core.agent import Agent

MODEL = "deepseek-v3-250324"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
API_KEY = os.environ.get("OPENAI_API_KEY", "test-key")


class MovieRecommendation(BaseModel):
    title: str
    year: int
    genre: str
    rating: float
    why_recommended: str


def test_structured_output():
    """Test that structured output works even when LLM wraps JSON in markdown"""
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

    # Verify it's actually a Pydantic model
    assert isinstance(movie, MovieRecommendation)
    assert movie.title
    assert movie.year > 1900
    print("✅ Test passed! Structured output working correctly.")


if __name__ == "__main__":
    test_structured_output()
