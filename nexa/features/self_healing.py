import asyncio
import logging
import traceback
from typing import Callable, Any, Dict, List, Optional
from nexa.features.tool_discovery import AutonomousToolDiscovery

logger = logging.getLogger(__name__)

class SelfHealingLoop:
    """
    Monitor task execution and automatically attempt fixes on failure
    """

    def __init__(self, engine=None):
        self.engine = engine
        self.tool_discovery = AutonomousToolDiscovery()
        self.max_retries = 3
        self.failure_history = []

    async def run_with_healing(self, func: Callable, *args, **kwargs) -> Any:
        """
        Run a function with self-healing capabilities
        """
        retry_count = 0
        last_error = None

        while retry_count < self.max_retries:
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                retry_count += 1
                last_error = e
                error_type = type(e).__name__
                error_msg = str(e)
                stack_trace = traceback.format_exc()

                logger.warning(f"⚠️ Task failed (Attempt {retry_count}/{self.max_retries}): {error_type}: {error_msg}")

                # Analyze failure and attempt fix
                fixed = await self._attempt_fix(e, stack_trace, args, kwargs)

                if not fixed:
                    logger.error(f"❌ Could not automatically fix the issue.")
                    # If we can't fix it, might as well break or try one last time if it's a transient error
                    if retry_count >= self.max_retries:
                        break
                else:
                    logger.info("🔧 Fix attempted, retrying task...")

        # If we reached here, healing failed
        self.failure_history.append({
            'error': str(last_error),
            'retry_count': retry_count,
            'success': False
        })
        raise last_error

    async def _attempt_fix(self, error: Exception, stack_trace: str, args, kwargs) -> bool:
        """
        Analyze error and attempt a fix
        """
        error_msg = str(error)

        # 1. Missing Module Error
        if isinstance(error, (ImportError, ModuleNotFoundError)):
            # Extract module name
            import re
            match = re.search(r"No module named '([^']+)'", error_msg)
            if match:
                module_name = match.group(1)
                return await self.tool_discovery.discover_and_install(module_name)

        # 2. Connection Errors
        if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            # Wait and retry
            await asyncio.sleep(2 ** (self.max_retries - 1)) # Exponential backoff
            return True

        # 3. Syntax or Logic Errors in generated code (if engine is available)
        if self.engine and ("SyntaxError" in stack_trace or "NameError" in stack_trace):
            # We could ask the LLM to fix the code
            # This is more advanced and requires integration with the engine's planning/coding capability
            return await self._ask_llm_to_fix(stack_trace, args, kwargs)

        return False

    async def _ask_llm_to_fix(self, stack_trace: str, args, kwargs) -> bool:
        """
        Use the LLM to analyze the stack trace and fix the issue
        """
        if not self.engine:
            return False

        logger.info("🧠 Asking AI to analyze and fix the error...")

        # This is a stub for where we would call the engine to reformulate the plan or fix the code
        # In a real implementation, we'd pass the stack trace to the router
        return False
