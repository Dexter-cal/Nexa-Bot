import asyncio
import logging
import pytest
from epex.intelligence.router import EnhancedLLMRouter
from epex.memory.soul import SoulFile

logging.basicConfig(level=logging.INFO)

@pytest.mark.asyncio
async def test_aura_scaling():
    router = EnhancedLLMRouter()
    soul = SoulFile()

    # Test 1: Professional (Neutral)
    print("\n--- Test 1: Neutral ---")
    await router.execute("What is the weather today?")
    print(f"Current Aura: {soul.data['current_aura']}")

    # Test 2: Aggressive (Urgent)
    print("\n--- Test 2: Urgent ---")
    await router.execute("Hurry up and scan my system now!")
    print(f"Current Aura: {soul.data['current_aura']}")

    # Test 3: Empathetic (Stressed)
    print("\n--- Test 3: Stressed ---")
    await router.execute("I am so frustrated and angry with this error!")
    print(f"Current Aura: {soul.data['current_aura']}")

    # Test 4: Witty (Funny)
    print("\n--- Test 4: Funny ---")
    await router.execute("Tell me a funny joke lol")
    print(f"Current Aura: {soul.data['current_aura']}")

if __name__ == "__main__":
    asyncio.run(test_aura_scaling())
