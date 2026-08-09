"""
AuthorizedToolExecutor — DI wrapper enforcing permission checks
before delegating to the concrete IToolExecutor.

Fail-closed: unknown/unauthorized tools return ToolResult(error=...).
Phase 3B IToolExecutor.execute_tool() signature: UNCHANGED.

Import namespace: runtime.policy.authorized_executor
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.python.contracts.tool import ToolResult

if TYPE_CHECKING:
    from core.python.contracts.tool import IToolExecutor
    from runtime.policy.gateway import PermissionGateway

logger = logging.getLogger("atlas.policy.authorized_executor")


class AuthorizedToolExecutor:
    """Implements IToolExecutor (duck-typed). Enforces policy before execution."""

    def __init__(
        self,
        inner: "IToolExecutor",
        gateway: "PermissionGateway",
        session_id: str,
        bus: "EventBus" = None,
        state: "StateManager" = None,
        exec_id: str = None
    ) -> None:
        self._inner = inner
        self._gateway = gateway
        self._session_id = session_id
        self._bus = bus
        self._state = state
        self._exec_id = exec_id

    async def execute_tool(self, name: str, arguments: dict) -> ToolResult:
        if not self._gateway.is_authorized(self._session_id, name):
            logger.warning(f"AuthorizedExecutor: DENY tool={name!r} session={self._session_id!r}")
            return ToolResult(
                result="",
                error=f"Tool '{name}' is not authorized for this session."
            )
            
        # Check if the tool requires manual approval
        # For Phase 8.5: we ask for approval for tools like run_command
        # We can use _TOOL_SCOPES from gateway to check if it's DANGEROUS
        from runtime.policy.gateway import _TOOL_SCOPES
        scope = _TOOL_SCOPES.get(name, "SAFE")
        
        if scope in ["DANGEROUS", "WRITE", "BROWSER"] and self._bus and self._state and self._exec_id:
            import asyncio
            import uuid
            import json
            
            # Setup future for this tool execution
            future = asyncio.Future()
            self._state.set(f"{self._exec_id}_approval_future", future)
            
            # Request approval over the bus
            await self._bus.publish("tool_approval", {
                "exec_id": self._exec_id,
                "tool_name": name,
                "arguments": arguments,
            })
            
            # Wait for approval (timeout after 5 minutes)
            try:
                approved = await asyncio.wait_for(future, timeout=300.0)
                if not approved:
                    return ToolResult(result="", error="Tool execution was rejected by the user.")
            except asyncio.TimeoutError:
                return ToolResult(result="", error="Tool execution approval timed out.")
            finally:
                self._state.delete(f"{self._exec_id}_approval_future")

        return await self._inner.execute_tool(name, arguments)
