import pytest
import asyncio
from epex.core.engine import engine
from epex.foundation.storage import SecureConfigStorage

@pytest.mark.asyncio
async def test_shadow_autonomy():
    storage = SecureConfigStorage()
    await storage.store_config({"user_name": "Max", "epex_name": "Bill", "return_reports": []})

    # Trigger ghost mode
    result = await engine.execute_command("ghost mode check system info")
    assert result['success']
    assert "Ghost Mode Activated" in result['response']

    # Simulate task completion (normally backgrounded)
    # Since we can't easily wait for a real background task in a unit test without mocking
    # we'll check if the logic for logging reports works
    from epex.models.core import Task
    dummy_task = Task(id=999, description="test task", status="completed")
    engine.task_manager.shadow_tasks.append(dummy_task.id)

    await engine.task_manager._log_to_return_report(dummy_task, "Done everything!")

    # Request return report
    result = await engine.execute_command("return report")
    assert result['success']
    assert "EPEX RETURN REPORT" in result['response']
    assert "Done everything!" in result['response']

@pytest.mark.asyncio
async def test_memory_indexing():
    # Force start engine if not already started
    if not engine.running:
        await engine.start()

    # Manually process to avoid background loop issues in pytest
    task = await engine.task_manager.create_task_from_command("memory index directory .")
    await engine.task_manager.process_queue()

    from epex.core.database import AsyncSessionLocal
    from epex.models.core import Task
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Task).where(Task.id == task.id))
        updated_task = result.scalars().first()
        assert updated_task.status == 'completed'
        assert updated_task.result['success'] is True
        assert "indexed" in updated_task.result['response'].lower()
