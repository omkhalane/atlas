"""
ExecutionScope — carries the shared deadline and cancellation signal
for a single top-level agent execution and all its children.

Design rules:
  • Identity fields are safe to copy.
  • asyncio primitives (_cancel_event) are NEVER copied; they are shared.
  • child_of() inherits the parent's absolute deadline and cancel event.
  • Never reset the deadline in child scopes.
"""
from __future__ import annotations

import asyncio
import copy
import time
from dataclasses import dataclass, field
from typing import Optional

from core.python.agents.core_types.errors import ExecutionCancelledError


@dataclass
class ExecutionScope:
    # ── Identity (immutable, safe to compare/repr) ──
    agent_id: str
    session_id: str
    workspace_id: str
    execution_id: str
    conversation_id: str

    # ── Shared execution primitives (NEVER deep-copied) ──
    _cancel_event: asyncio.Event = field(
        default_factory=asyncio.Event, repr=False, compare=False, hash=False
    )
    _deadline_monotonic: float = field(
        default_factory=lambda: time.monotonic() + 300.0,
        repr=False, compare=False, hash=False
    )

    # ────────────────────────────────────────────
    def remaining(self) -> float:
        """Seconds remaining before the absolute deadline. Floored at 0."""
        return max(0.0, self._deadline_monotonic - time.monotonic())

    def is_expired(self) -> bool:
        return self.remaining() == 0.0

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def cancel(self) -> None:
        """External callers (VS Code Stop, deadline watchdog) call this."""
        self._cancel_event.set()

    def check_cancellation(self) -> None:
        """Call at the top of every agent loop iteration."""
        if self._cancel_event.is_set():
            raise ExecutionCancelledError("Execution was cancelled.")
        if self.is_expired():
            self.cancel()
            raise ExecutionCancelledError("Execution deadline exceeded.")

    # ────────────────────────────────────────────
    @classmethod
    def create(
        cls,
        *,
        agent_id: str,
        session_id: str,
        workspace_id: str,
        execution_id: str,
        conversation_id: str,
        deadline_seconds: float = 300.0,
    ) -> "ExecutionScope":
        """Create a root execution scope with a fresh deadline and cancel event."""
        return cls(
            agent_id=agent_id,
            session_id=session_id,
            workspace_id=workspace_id,
            execution_id=execution_id,
            conversation_id=conversation_id,
            _cancel_event=asyncio.Event(),
            _deadline_monotonic=time.monotonic() + deadline_seconds,
        )

    @classmethod
    def child_of(cls, parent: "ExecutionScope", *, agent_id: str) -> "ExecutionScope":
        """
        Create a child scope that SHARES the parent's cancel event and deadline.
        The child's deadline is NEVER reset — it inherits the parent's absolute value.
        """
        return cls(
            agent_id=agent_id,
            session_id=parent.session_id,
            workspace_id=parent.workspace_id,
            execution_id=parent.execution_id,
            conversation_id=parent.conversation_id,
            _cancel_event=parent._cancel_event,          # shared reference
            _deadline_monotonic=parent._deadline_monotonic,  # inherited, never extended
        )

    # ────────────────────────────────────────────
    def __deepcopy__(self, memo):
        raise TypeError(
            "ExecutionScope must not be deep-copied: asyncio.Event is not copyable. "
            "Use child_of() to derive child scopes."
        )
