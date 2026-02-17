import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from nexa.core.alerts import alert_manager

@pytest.mark.asyncio
async def test_alert_emission():
    # Mock communication tool
    from nexa.tools.registry import registry
    mock_tool = AsyncMock()
    mock_tool.execute.return_value = MagicMock(success=True)

    with patch.object(registry, 'get', return_value=mock_tool):
        await alert_manager.emit(
            title="Test Critical Alert",
            message="Something happened",
            severity="critical"
        )

        assert len(alert_manager.history) > 0
        assert alert_manager.history[-1].title == "Test Critical Alert"
        mock_tool.execute.assert_called()

@pytest.mark.asyncio
async def test_alert_routing_low_severity():
    from nexa.tools.registry import registry
    mock_tool = AsyncMock()

    with patch.object(registry, 'get', return_value=mock_tool):
        await alert_manager.emit(
            title="Low alert",
            message="Info only",
            severity="info"
        )
        mock_tool.execute.assert_not_called()
