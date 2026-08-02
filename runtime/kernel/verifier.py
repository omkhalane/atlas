"""
Phase E: Verification Engine

Pure deterministic verification — no LLM involved.
After every execution step, the runtime verifies the action actually happened.
On failure: publishes STEP_FAILED to EventBus for retry/rollback.
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("atlas.verifier")


class VerificationResult:
    def __init__(self, success: bool, reason: str = "", should_retry: bool = False):
        self.success = success
        self.reason = reason
        self.should_retry = should_retry

    def __repr__(self):
        return f"VerificationResult(success={self.success}, reason='{self.reason}')"


class VerificationEngine:
    """
    Deterministic post-execution verifier.
    Each capability type has its own verification logic.
    The LLM is NEVER involved here — pure deterministic checks.
    """

    def verify(self, capability_id: str, action: str, parameters: Dict[str, Any], result: Any) -> VerificationResult:
        verifier = getattr(self, f"_verify_{capability_id.replace('-', '_')}", None)
        if verifier:
            try:
                return verifier(action, parameters, result)
            except Exception as e:
                logger.error(f"Verifier exception for {capability_id}.{action}: {e}")
                return VerificationResult(False, f"Verifier crashed: {e}", should_retry=False)

        # No specific verifier — pass through (unknown capabilities)
        return VerificationResult(True, "No verifier — passthrough")

    # ── Filesystem ──────────────────────────────────────────────────────────

    def _verify_filesystem(self, action: str, params: Dict, result: Any) -> VerificationResult:
        if action == "write_file":
            path = params.get("path")
            if not path:
                return VerificationResult(False, "No path in parameters")
            if os.path.exists(path):
                return VerificationResult(True, f"File exists: {path}")
            return VerificationResult(False, f"File not found after write: {path}", should_retry=True)

        if action == "delete_file":
            path = params.get("path")
            if not path:
                return VerificationResult(False, "No path in parameters")
            if not os.path.exists(path):
                return VerificationResult(True, f"File deleted: {path}")
            return VerificationResult(False, f"File still exists after delete: {path}", should_retry=True)

        if action == "list_files":
            if result and hasattr(result, 'success') and result.success:
                return VerificationResult(True, "File list retrieved")
            return VerificationResult(False, "File list empty or error", should_retry=True)

        if action == "append_file":
            path = params.get("path")
            if path and os.path.exists(path):
                return VerificationResult(True, f"Append target exists: {path}")
            return VerificationResult(False, f"Append target not found: {path}", should_retry=False)

        return VerificationResult(True, f"Filesystem {action} — no specific check")

    # ── Command / Terminal ───────────────────────────────────────────────────

    def _verify_command(self, action: str, params: Dict, result: Any) -> VerificationResult:
        if action == "run":
            if result and hasattr(result, 'success'):
                if result.success:
                    return VerificationResult(True, "Command completed successfully")
                else:
                    # Non-zero exit — retry once
                    return VerificationResult(False, f"Command failed: {getattr(result, 'error', 'unknown')}", should_retry=True)
        return VerificationResult(True, "Command — no specific check")

    # ── Memory ───────────────────────────────────────────────────────────────

    def _verify_memory(self, action: str, params: Dict, result: Any) -> VerificationResult:
        if action == "store":
            if result and hasattr(result, 'success') and result.success:
                return VerificationResult(True, "Memory stored")
            return VerificationResult(False, "Memory store failed", should_retry=True)
        return VerificationResult(True, "Memory — no specific check")

    # ── Browser ──────────────────────────────────────────────────────────────

    def _verify_browser(self, action: str, params: Dict, result: Any) -> VerificationResult:
        if result and hasattr(result, 'success'):
            if result.success:
                return VerificationResult(True, "Browser action succeeded")
            # Browser failures: retry with vision mode flag
            return VerificationResult(False, f"Browser action failed: {getattr(result, 'error', 'unknown')}", should_retry=True)
        return VerificationResult(True, "Browser — no specific check")

    # ── Search ───────────────────────────────────────────────────────────────

    def _verify_search(self, action: str, params: Dict, result: Any) -> VerificationResult:
        if result and hasattr(result, 'success') and result.success:
            data = getattr(result, 'data', {})
            count = len(data.get("results", [])) if isinstance(data, dict) else 0
            if count == 0:
                return VerificationResult(False, "Search returned no results", should_retry=False)
            return VerificationResult(True, f"Search returned {count} results")
        return VerificationResult(False, "Search failed", should_retry=True)
