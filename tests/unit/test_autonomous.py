import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from nexa.features.tool_discovery import AutonomousToolDiscovery
from nexa.features.self_healing import SelfHealingLoop

@pytest.mark.asyncio
async def test_tool_discovery_install():
    discovery = AutonomousToolDiscovery()

    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"Success", b"")
        mock_process.returncode = 0
        mock_exec.return_value = mock_process

        result = await discovery.discover_and_install("nonexistent_package")
        assert result is True
        assert "nonexistent_package" in discovery.installed_this_session

@pytest.mark.asyncio
async def test_self_healing_module_not_found():
    healing = SelfHealingLoop()

    # Mock tool discovery
    healing.tool_discovery.discover_and_install = AsyncMock(return_value=True)

    mock_func = AsyncMock()
    # First call fails, second call succeeds
    mock_func.side_effect = [ModuleNotFoundError("No module named 'missing'"), "Success"]

    result = await healing.run_with_healing(mock_func)

    assert result == "Success"
    assert mock_func.call_count == 2
    healing.tool_discovery.discover_and_install.assert_called_with("missing")

@pytest.mark.asyncio
async def test_self_healing_retry_backoff():
    healing = SelfHealingLoop()
    healing.max_retries = 2

    mock_func = AsyncMock()
    mock_func.side_effect = Exception("Transient error")

    with pytest.raises(Exception) as excinfo:
        await healing.run_with_healing(mock_func)

    assert "Transient error" in str(excinfo.value)
    assert mock_func.call_count == 2 # Initial + 1 retry
