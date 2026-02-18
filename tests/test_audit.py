import pytest
import asyncio
from nexa.core.engine import engine
from nexa.foundation.storage import SecureConfigStorage

@pytest.mark.asyncio
async def test_personalization():
    storage = SecureConfigStorage()
    await storage.store_config({"user_name": "Max", "nexa_name": "Bill"})

    # Test greeting
    result = await engine.execute_command("hi")
    assert result['success']
    assert "hi sir" in result['response'].lower()

    # Test name change
    result = await engine.execute_command("my name is John")
    assert result['success']
    assert "hi John" in result['response']

    config = await storage.load_config()
    assert config['user_name'] == "John"

@pytest.mark.asyncio
async def test_dream_engine():
    result = await engine.execute_command("simulate task build a space elevator")
    assert result['success']
    assert "response" in result
