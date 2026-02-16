import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityGuardian:
    """Enforces security policies and guardrails"""

    def __init__(self, config: Dict):
        self.config = config
        self.policies = config.get('security', {})
        self.audit_log = []

    def assess_risk(self, action: str, params: Dict[str, Any]) -> RiskLevel:
        """Assess risk level of an action"""

        # Critical actions
        if action in ['file.delete', 'system.shutdown', 'cloud.create_instance']:
            path = str(params.get('path', ''))
            if self._is_system_path(path):
                return RiskLevel.CRITICAL
            return RiskLevel.HIGH

        # High risk actions
        elif action in ['system.run_command', 'dev.git_push', 'comm.send_email']:
            return RiskLevel.HIGH

        # Medium risk actions
        elif action in ['file.write', 'web.post', 'browser.click']:
            return RiskLevel.MEDIUM

        # Low risk by default
        else:
            return RiskLevel.LOW

    def require_approval(self, action: str, risk: RiskLevel) -> bool:
        """Check if action requires human approval"""

        if risk == RiskLevel.CRITICAL:
            return True
        elif risk == RiskLevel.HIGH:
            return self.policies.get('approve_high_risk', True)
        elif risk == RiskLevel.MEDIUM:
            return self.policies.get('approve_medium_risk', False)
        else:
            return False

    def enforce_policy(self, action: str, params: Dict) -> bool:
        """Check if action violates any policy"""

        # Check blocked commands
        if action == 'system.run_command':
            command = params.get('command', '')
            blocked = self.policies.get('blocked_commands', [])
            if any(cmd in command for cmd in blocked):
                return False

        # Check file path restrictions
        if action.startswith('file.'):
            path = params.get('path', '')
            if self._is_restricted_path(path):
                return False

        return True

    def log_action(self, action: str, params: Dict, result: Any, risk: RiskLevel, task_id: Optional[str] = None, user_id: Optional[str] = None):
        """Log action to audit trail"""

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'params': params,
            'risk_level': risk.value,
            'success': result.success if hasattr(result, 'success') else True,
            'error': result.error if hasattr(result, 'error') else None
        }

        self.audit_log.append(log_entry)

        # Async persist to DB
        import asyncio
        from nexa.models.extended import Action
        from nexa.core.database import AsyncSessionLocal

        async def persist():
            try:
                async with AsyncSessionLocal() as session:
                    db_action = Action(
                        user_id=user_id,
                        task_id=task_id,
                        action_type=action,
                        description=f"Executed tool {action}",
                        parameters=params,
                        result=result.model_dump() if hasattr(result, 'model_dump') else result,
                        status='success' if log_entry['success'] else 'failed'
                    )
                    session.add(db_action)
                    await session.commit()
            except Exception as e:
                logger.error(f"Failed to persist action to DB: {e}")

        asyncio.create_task(persist())
        logger.info(f"Audit Log: {json.dumps(log_entry)}")

    def _is_system_path(self, path: str) -> bool:
        """Check if path is a critical system path"""
        system_paths = ['/system', '/windows', '/boot', '/etc', 'C:\\Windows']
        return any(sp in path.lower() for sp in system_paths)

    def _is_restricted_path(self, path: str) -> bool:
        """Check if path is restricted"""
        restricted = self.policies.get('restricted_paths', [])
        return any(rp in path for rp in restricted)

class GuardrailEngine:
    """Intelligently configure based on context and natural language rules"""

    def __init__(self):
        self.rules = []

    async def add_rule(self, rule_text: str):
        # Simplified: in a real scenario, this would use NLP to parse the rule
        self.rules.append(rule_text)
        logger.info(f"Added guardrail rule: {rule_text}")

    async def check_action(self, action_context: Dict) -> Dict:
        """Check if an action is allowed by any rules"""
        # Basic check for now
        for rule in self.rules:
            if "never delete" in rule.lower() and action_context.get('action') == 'file.delete':
                return {"allowed": False, "violation": rule}

        return {"allowed": True}
