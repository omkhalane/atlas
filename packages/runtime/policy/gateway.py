"""
PermissionGateway — implements IPermissionGateway.

Evaluates tool execution requests against the SessionPolicyRegistry.
Fail-closed: unknown tools and missing policy both produce DENY.

Import namespace: runtime.policy.gateway
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.policy.store import SessionPolicyRegistry

logger = logging.getLogger("atlas.policy.gateway")

# Tool → scope mapping (populated from tool registry)
_TOOL_SCOPES: dict[str, str] = {
    # Safe tools — read-only, no side effects
    "read_file":       "SAFE",
    "list_directory":  "SAFE",
    "search":          "SAFE",
    "get_content":     "SAFE",
    # Read tools — read external state
    "http_get":        "READ",
    "web_search":      "READ",
    # Write tools — mutate local state
    "write_file":      "WRITE",
    "create_file":     "WRITE",
    "delete_file":     "WRITE",
    "filesystem":      "WRITE",  # the capability name
    # Browser tools
    "navigate":        "BROWSER",
    "click":           "BROWSER",
    "screenshot":      "BROWSER",
    "browser":         "BROWSER", # the capability name
    "mcp_chrome-devtools": "BROWSER",
    # Shell/process tools
    "run_command":     "DANGEROUS",
    "execute_shell":   "DANGEROUS",
    "command":         "DANGEROUS", # the capability name
}

_SCOPE_ORDER = ["SAFE", "READ", "WRITE", "BROWSER", "NETWORK", "DANGEROUS"]


class PermissionGateway:
    """
    Fail-closed permission gateway.
    Unknown tool → DENY.
    Missing policy → SAFE-only.
    """

    def __init__(self, policy_registry: "SessionPolicyRegistry") -> None:
        self._registry = policy_registry

    def is_authorized(self, session_id: str, tool_name: str) -> bool:
        tool_scope = _TOOL_SCOPES.get(tool_name)
        if tool_scope is None:
            logger.warning(f"PermissionGateway: unknown tool '{tool_name}' → DENY")
            return False

        permitted = self._registry.get_permitted_scopes(session_id)
        authorized = tool_scope in permitted
        if not authorized:
            logger.warning(
                f"PermissionGateway: session={session_id!r} tool={tool_name!r} "
                f"scope={tool_scope!r} not in {permitted} → DENY"
            )
        return authorized
