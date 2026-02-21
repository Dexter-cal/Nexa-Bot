import pytest
import asyncio
from epex.core.engine import engine
from epex.foundation.storage import SecureConfigStorage

@pytest.mark.asyncio
async def test_personalization():
    storage = SecureConfigStorage()
    await storage.store_config({"user_name": "Max", "epex_name": "Bill"})

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
    # Force start engine if not already started
    if not engine.running:
        await engine.start()

    # Manually process to avoid background loop issues in pytest
    task = await engine.task_manager.create_task_from_command("simulate task build a space elevator")
    await engine.task_manager.process_queue()

    from epex.core.database import AsyncSessionLocal
    from epex.models.core import Task
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Task).where(Task.id == task.id))
        updated_task = result.scalars().first()
        assert updated_task.status == 'completed'
        assert updated_task.result['success'] is True
