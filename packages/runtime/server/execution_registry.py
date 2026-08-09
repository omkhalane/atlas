"""
ExecutionRegistry — maps execution_id → ExecutionScope.

Used by the JSON-RPC handler to route a VS Code Stop/Cancel request
to the correct in-flight execution scope.
"""
from __future__ import annotations

from typing import Dict, Optional
from core.python.agents.core_types.scope import ExecutionScope


class ExecutionRegistry:
    def __init__(self) -> None:
        self._scopes: Dict[str, ExecutionScope] = {}

    def register(self, scope: ExecutionScope) -> None:
        self._scopes[scope.execution_id] = scope

    def cancel(self, execution_id: str) -> bool:
        """
        Cancel a running execution. Returns True if found, False if not found.
        VS Code JSON-RPC handler calls this on execution/cancel.
        """
        scope = self._scopes.get(execution_id)
        if scope is None:
            return False
        scope.cancel()
        return True

    def unregister(self, execution_id: str) -> None:
        self._scopes.pop(execution_id, None)

    def get(self, execution_id: str) -> Optional[ExecutionScope]:
        return self._scopes.get(execution_id)
