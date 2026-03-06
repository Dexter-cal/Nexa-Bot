import pytest
import asyncio
from epex.core.engine import engine
from epex.core.security import RiskLevel

@pytest.mark.asyncio
async def test_immune_system():
    # Quarantine a tool
    engine.security_guardian.quarantine_tool("system.run_command", "Testing quarantine")

    # Try to use it
    risk = engine.security_guardian.assess_risk("system.run_command", {})
    assert risk == RiskLevel.CRITICAL

    # Remove from quarantine for other tests
    engine.security_guardian.quarantined_tools.remove("system.run_command")

@pytest.mark.asyncio
async def test_tool_sharing_interface():
    # Check if tools are registered
    from epex.tools.registry import registry
    assert registry.get("meta.share_tool") is not None
    assert registry.get("meta.request_tool") is not None
    assert registry.get("meta.ethereal_sync") is not None

@pytest.mark.asyncio
async def test_new_maint_tools():
    from epex.tools.registry import registry
    assert registry.get("maint.deep_scrub") is not None
    assert registry.get("security.firewall_override") is not None
    assert registry.get("meta.logic_refactor") is not None
