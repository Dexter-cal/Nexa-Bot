import pytest
from nexa.core.security import SecurityGuardian, RiskLevel

class TestSecurityGuardian:
    @pytest.fixture
    def guardian(self):
        return SecurityGuardian({})

    def test_assess_risk(self, guardian):
        # Low risk
        assert guardian.assess_risk("system.info", {}) == RiskLevel.LOW

        # High risk
        assert guardian.assess_risk("file.delete", {"path": "/home/user/test.txt"}) == RiskLevel.HIGH

        # Critical risk
        assert guardian.assess_risk("file.delete", {"path": "/etc/passwd"}) == RiskLevel.CRITICAL

    def test_require_approval(self, guardian):
        assert guardian.require_approval("file.delete", RiskLevel.CRITICAL) is True
        assert guardian.require_approval("system.info", RiskLevel.LOW) is False
