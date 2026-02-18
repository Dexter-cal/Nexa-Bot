import pytest
import asyncio
from nexa.core.engine import engine
from nexa.foundation.storage import SecureConfigStorage

@pytest.mark.asyncio
async def test_shadow_autonomy():
    storage = SecureConfigStorage()
    await storage.store_config({"user_name": "Max", "nexa_name": "Bill", "return_reports": []})

    # Trigger ghost mode
    result = await engine.execute_command("ghost mode check system info")
    assert result['success']
    assert "Ghost Mode Activated" in result['response']

    # Simulate task completion (normally backgrounded)
    # Since we can't easily wait for a real background task in a unit test without mocking
    # we'll check if the logic for logging reports works
    from nexa.models.core import Task
    dummy_task = Task(id=999, description="test task", status="completed")
    engine.task_manager.shadow_tasks.append(dummy_task.id)

    await engine.task_manager._log_to_return_report(dummy_task, "Done everything!")

    # Request return report
    result = await engine.execute_command("return report")
    assert result['success']
    assert "NEXA RETURN REPORT" in result['response']
    assert "Done everything!" in result['response']

@pytest.mark.asyncio
async def test_memory_indexing():
    # Test memory indexing tool (mocked effect)
    result = await engine.execute_command("memory index directory .")
    assert result['success']
    assert "Successfully indexed" in result['response']
