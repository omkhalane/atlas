"""
TraceContext — carries active execution metadata through asyncio ContextVar.

Allows EnvelopedEventBus to auto-stamp events with correlation identifiers
without changing the EventBus.publish() signature.

Import namespace: `runtime.observability.trace_context`
"""
from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

# Holds (execution_id, conversation_id, agent_id) for the current coroutine.
# None when called outside an execution context.
_active: ContextVar[Optional[dict]] = ContextVar("atlas_trace_ctx", default=None)


def set_trace(execution_id: str, conversation_id: str, agent_id: str,
              session_id: str = "", workspace_id: str = "") -> None:
    """Establish trace context for this coroutine and its children."""
    _active.set({
        "execution_id": execution_id,
        "conversation_id": conversation_id,
        "agent_id": agent_id,
        "session_id": session_id,
        "workspace_id": workspace_id,
    })


def clear_trace() -> None:
    """Clear the trace context (call in finally blocks)."""
    _active.set(None)


def get_envelope() -> dict:
    """Return current trace metadata dict; empty dict if no context active."""
    ctx = _active.get()
    return dict(ctx) if ctx else {}
