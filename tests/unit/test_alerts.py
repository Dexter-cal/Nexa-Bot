import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from epex.core.alerts import alert_manager

@pytest.mark.asyncio
async def test_alert_emission():
    # Mock communication hub
    from epex.core.engine import engine
    mock_hub = AsyncMock()

    with patch.object(engine, 'messaging_hub', mock_hub):
        await alert_manager.emit(
            title="Test Critical Alert",
            message="Something happened",
            severity="critical"
        )

        assert len(alert_manager.history) > 0
        assert alert_manager.history[-1].title == "Test Critical Alert"
        mock_hub.notify.assert_called()

@pytest.mark.asyncio
async def test_alert_routing_low_severity():
    from epex.core.engine import engine
    mock_hub = AsyncMock()

    with patch.object(engine, 'messaging_hub', mock_hub):
        await alert_manager.emit(
            title="Low alert",
            message="Info only",
            severity="info"
        )
        mock_hub.notify.assert_not_called()
