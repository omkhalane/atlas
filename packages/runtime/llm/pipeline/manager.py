"""
Pipeline Manager
Executes pre-processors, request execution, stream management, and post-processors.
"""
from typing import List
from runtime.llm.contracts import ExecutionContext, LLMMessage, LLMResponse
from runtime.llm.pipeline.middleware import BaseMiddleware, LoggingMiddleware, CostTrackingMiddleware


class PipelineManager:
    def __init__(self, capability_registry=None):
        self.middlewares: List[BaseMiddleware] = [
            LoggingMiddleware(),
            CostTrackingMiddleware(capability_registry)
        ]

    def add_middleware(self, middleware: BaseMiddleware):
        self.middlewares.append(middleware)

    async def run_preprocessors(self, ctx: ExecutionContext, messages: List[LLMMessage]) -> List[LLMMessage]:
        curr = messages
        for m in self.middlewares:
            curr = await m.process_request(ctx, curr)
        return curr

    async def run_postprocessors(self, ctx: ExecutionContext, response: LLMResponse) -> LLMResponse:
        curr = response
        for m in reversed(self.middlewares):
            curr = await m.process_response(ctx, curr)
        return curr
