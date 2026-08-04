"""
Middleware Pipeline Components
"""
import logging
from abc import ABC, abstractmethod
from typing import List
from runtime.llm.contracts import ExecutionContext, LLMMessage, LLMResponse

logger = logging.getLogger("atlas.llm.middleware")


class BaseMiddleware(ABC):
    async def process_request(self, ctx: ExecutionContext, messages: List[LLMMessage]) -> List[LLMMessage]:
        return messages

    async def process_response(self, ctx: ExecutionContext, response: LLMResponse) -> LLMResponse:
        return response


class LoggingMiddleware(BaseMiddleware):
    async def process_request(self, ctx: ExecutionContext, messages: List[LLMMessage]) -> List[LLMMessage]:
        logger.info(f"[{ctx.request_id}] Pre-processing request ({len(messages)} msgs) | task={ctx.task_type}")
        return messages

    async def process_response(self, ctx: ExecutionContext, response: LLMResponse) -> LLMResponse:
        logger.info(f"[{ctx.request_id}] Post-processing response | tokens={response.usage.total_tokens} | cost=${response.usage.estimated_cost_usd:.6f}")
        return response


class CostTrackingMiddleware(BaseMiddleware):
    def __init__(self, capability_registry=None):
        self.registry = capability_registry

    async def process_response(self, ctx: ExecutionContext, response: LLMResponse) -> LLMResponse:
        if self.registry and response.model and response.provider_id:
            cost = self.registry.calculate_cost(
                response.provider_id,
                response.model,
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
            response.usage.estimated_cost_usd = cost
        return response
