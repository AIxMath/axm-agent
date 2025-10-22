"""Example: Async and streaming"""

import asyncio
from axm import Agent

agent = Agent("gpt-4")


@agent.tool
def get_data(source: str) -> str:
    """Get data from a source"""
    return f"Data retrieved from {source}"


async def async_example():
    """Demonstrate async capabilities"""
    print("⚡ Async Example\n")

    # Async single call
    response = await agent.arun("Tell me a short story about a robot")
    print("Async response:")
    print(response)
    print()


async def streaming_example():
    """Demonstrate streaming capabilities"""
    print("🌊 Streaming Example\n")

    print("Streaming response: ")
    async for chunk in agent.astream("Write a haiku about programming"):
        print(chunk, end="", flush=True)
    print("\n")


def sync_streaming_example():
    """Demonstrate sync streaming"""
    print("🌊 Sync Streaming Example\n")

    print("Streaming response: ")
    for chunk in agent.stream("Count from 1 to 5 slowly"):
        print(chunk, end="", flush=True)
    print("\n")


async def concurrent_example():
    """Run multiple agents concurrently"""
    print("🔄 Concurrent Example\n")

    agent1 = Agent("gpt-4")
    agent2 = Agent("gpt-4")
    agent3 = Agent("gpt-4")

    # Run multiple agents in parallel
    results = await asyncio.gather(
        agent1.arun("What is Python?"),
        agent2.arun("What is JavaScript?"),
        agent3.arun("What is Rust?"),
    )

    print("Results from concurrent execution:")
    for i, result in enumerate(results, 1):
        print(f"\nAgent {i}: {result[:100]}...")


if __name__ == "__main__":
    print("="*60)

    # Run sync streaming first
    sync_streaming_example()

    print("="*60)

    # Run async examples
    asyncio.run(async_example())

    print("="*60)

    asyncio.run(streaming_example())

    print("="*60)

    asyncio.run(concurrent_example())

    print("="*60)
