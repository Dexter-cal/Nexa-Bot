import pytest
from unittest.mock import Mock, AsyncMock, patch
from epex.core.task_manager import TaskManager, Task

class TestTaskManager:
    @pytest.fixture
    def task_manager(self):
        return TaskManager()

    @pytest.mark.asyncio
    async def test_create_task(self, task_manager):
        from epex.core.database import init_db
        await init_db()
        task = await task_manager.create_task_from_command("test command")
        assert task.description == "test command"
        assert task.status == "pending"
        assert task_manager.queue.qsize() == 1

    @pytest.mark.asyncio
    async def test_process_queue(self, task_manager):
        from epex.core.database import init_db, AsyncSessionLocal
        from sqlalchemy import select
        from epex.models.core import Task as DBTask
        await init_db()
        task = await task_manager.create_task_from_command("system info")

        with patch.object(task_manager, 'execute_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"success": True}
            await task_manager.process_queue()

            async with AsyncSessionLocal() as session:
                result = await session.execute(select(DBTask).where(DBTask.id == task.id))
                updated_task = result.scalars().first()
                assert updated_task.status == "completed"
                assert updated_task.result == {"success": True}

    @pytest.mark.asyncio
    async def test_execute_task_with_tools(self, task_manager):
        from epex.tools.registry import registry
        from epex.core.database import init_db
        await init_db()
        await registry.load_default_tools()

        task = await task_manager.create_task_from_command("system info")
        # Task manager should plan this to use system.info tool
        result = await task_manager.execute_task(task)
        assert result["success"] is True
        # steps are now dictionaries after serialization fix
        assert any(step.get("success") for step in result["steps"])
