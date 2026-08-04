"""
Stream Manager
Handles streaming tokens, reasoning chunks, cancellation detection, and listener dispatching.
"""
import asyncio
import logging
from typing import AsyncGenerator, Callable, Optional
from runtime.llm.contracts import ExecutionContext, LLMStreamChunk

logger = logging.getLogger("atlas.llm.streaming")


class StreamManager:
    def __init__(self):
        self._listeners: List[Callable[[ExecutionContext, LLMStreamChunk], None]] = []

    def add_listener(self, listener: Callable[[ExecutionContext, LLMStreamChunk], None]):
        self._listeners.append(listener)

    async def stream_with_cancellation(
        self,
        ctx: ExecutionContext,
        generator: AsyncGenerator[LLMStreamChunk, None]
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        try:
            async for chunk in generator:
                if ctx.cancellation_requested:
                    logger.info(f"Stream cancelled for request {ctx.request_id}")
                    yield LLMStreamChunk(finish_reason="cancelled")
                    break

                for listener in self._listeners:
                    try:
                        listener(ctx, chunk)
                    except Exception:
                        pass

                yield chunk
        except Exception as e:
            logger.error(f"Stream error for request {ctx.request_id}: {e}")
            raise
