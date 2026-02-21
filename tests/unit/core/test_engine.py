import pytest
from unittest.mock import Mock, AsyncMock, patch
from epex.core.engine import EpexEngine

class TestEpexEngine:
    """Test suite for EpexEngine"""

    @pytest.fixture
    def engine(self):
        """Create engine instance for testing"""
        return EpexEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes correctly"""
        assert engine is not None
        assert engine.running is False

    @pytest.mark.asyncio
    async def test_engine_start(self, engine):
        """Test engine starts successfully"""
        with patch('epex.core.database.init_db', new_callable=AsyncMock) as mock_db_init:
            with patch('epex.tools.registry.registry.load_default_tools', new_callable=AsyncMock) as mock_tool_load:
                # Start engine
                await engine.start()

                # Verify
                assert engine.running is True
                mock_db_init.assert_called_once()
                mock_tool_load.assert_called_once()

    @pytest.mark.asyncio
    async def test_engine_stop(self, engine):
        """Test engine stops cleanly"""
        engine.running = True
        engine.task_manager = Mock()
        engine.task_manager.cleanup = AsyncMock()

        await engine.stop()

        assert engine.running is False
        engine.task_manager.cleanup.assert_called_once()
