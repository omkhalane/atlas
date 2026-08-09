"""
TimedProviderWrapper — wraps IProviderManager with deadline enforcement.
"""
from __future__ import annotations

import asyncio
from typing import Any, TYPE_CHECKING

from core.python.agents.core_types.scope import ExecutionScope

if TYPE_CHECKING:
    from core.python.contracts.provider import IProviderManager


class TimedProviderWrapper:
    """Implements IProviderManager (duck-typed)."""

    def __init__(self, inner: "IProviderManager", scope: ExecutionScope) -> None:
        self._inner = inner
        self._scope = scope

    async def execute_prompt(self, route: Any, prompt: list, **kwargs: Any) -> Any:
        remaining = self._scope.remaining()
        if remaining == 0.0:
            raise TimeoutError("Provider deadline already exceeded.")
            
        async def _run():
            res = self._inner.execute_prompt(route, prompt, **kwargs)
            if asyncio.iscoroutine(res):
                return await res
            return res
            
        try:
            async with asyncio.timeout(remaining):
                return await _run()
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Provider call timed out after {remaining:.1f}s budget."
            ) from None

    # Passthrough for other provider methods (embeddings, etc.)
    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
