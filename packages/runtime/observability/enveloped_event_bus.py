"""
EnvelopedEventBus — wraps EventBus to auto-stamp trace metadata on every event.

Import namespace: `runtime.observability.enveloped_event_bus`

Contract: EventBus.publish(event_type, payload) signature UNCHANGED.
"""
from __future__ import annotations

from typing import Callable, Awaitable

from runtime.events.bus import EventBus
from runtime.observability.trace_context import get_envelope


class EnvelopedEventBus:
    """Duck-typed EventBus wrapper. Stamps trace context on every publish call."""

    def __init__(self, inner: EventBus) -> None:
        self._inner = inner

    async def publish(self, event_type: str, payload: dict) -> None:
        envelope = get_envelope()
        stamped = {**envelope, **payload}   # payload wins on key conflict
        await self._inner.publish(event_type, stamped)

    def publish_sync(self, event_type: str, payload: dict) -> None:
        """Sync variant used by crash handlers."""
        envelope = get_envelope()
        stamped = {**envelope, **payload}
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._inner.publish(event_type, stamped))
        except RuntimeError:
            pass

    def subscribe(self, event_type: str, handler: Callable[[dict], Awaitable[None]]) -> None:
        self._inner.subscribe(event_type, handler)

    def unsubscribe(self, event_type: str, handler: Callable[[dict], Awaitable[None]]) -> None:
        if hasattr(self._inner, "unsubscribe"):
            self._inner.unsubscribe(event_type, handler)
        else:
            # Fallback if inner EventBus also lacks it
            if event_type in self._inner.subscribers:
                try:
                    self._inner.subscribers[event_type].remove(handler)
                except ValueError:
                    pass

    async def start(self) -> None:
        await self._inner.start()

    def stop(self) -> None:
        self._inner.stop()

    @property
    def history(self):
        return self._inner.history
