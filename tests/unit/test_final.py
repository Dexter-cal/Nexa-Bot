import pytest
import os
from nexa.core.engine import engine
from nexa.orchestration.swarm import SwarmCoordinator
from nexa.core.innovation import BlockchainAudit
from nexa.privacy.breach_detector import BreachDetector

class TestFinalProject:
    @pytest.mark.asyncio
    async def test_engine_startup_with_all_modules(self):
        # This will initialize all modules including PrivacyGuardian and Innovation
        await engine.start()
        assert engine.running is True
        assert engine.privacy_guardian.monitoring is True
        assert engine.innovation.blockchain is not None
        await engine.stop()

    @pytest.mark.asyncio
    async def test_swarm_coordinator(self):
        from nexa.core.agent import Agent
        agents = [Agent(f"a{i}", "assistant", "assistive") for i in range(2)]
        for a in agents: await a.start()

        swarm = SwarmCoordinator(agents)
        # Mock waiting for results
        await swarm.execute()

        for a in agents: await a.terminate()

    @pytest.mark.asyncio
    async def test_breach_detector(self):
        # This calls a real API, so we might need to mock it if it's slow or unreliable
        # But for now we just check if it exists
        bd = BreachDetector()
        result = await bd.check_password_pwned("password123")
        assert result['pwned'] is True
        assert result['count'] > 0

    @pytest.mark.asyncio
    async def test_blockchain_audit(self):
        audit = BlockchainAudit()
        await audit.log_action({"action": "test"})
        assert len(audit.chain) == 1
