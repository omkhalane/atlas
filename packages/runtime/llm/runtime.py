"""
Central Unified LLM Runtime Core
Orchestrates language model calls across Atlas modules.
"""
import logging
from typing import List, Dict, Any, AsyncGenerator, Optional

from runtime.llm.contracts import (
    ExecutionContext, LLMMessage, LLMResponse, LLMStreamChunk,
    ToolDefinition, ProviderProfile
)
from runtime.llm.capabilities import ProviderCapabilityRegistry
from runtime.llm.model_registry import ModelRegistry
from runtime.llm.providers.provider_manager import ProviderManager
from runtime.llm.providers.provider_router import ProviderRouter
from runtime.llm.context.engine import ContextEngine
from runtime.llm.prompt.engine import PromptEngine
from runtime.llm.tools.adapter import ToolAdapter
from runtime.llm.pipeline.manager import PipelineManager
from runtime.llm.streaming.manager import StreamManager
from runtime.llm.conversation.service import ConversationService
from runtime.llm.conversation.session_initializer import SessionInitializer
from runtime.llm.background.worker import BackgroundWorkerPool

logger = logging.getLogger("atlas.llm.runtime")


class LLMRuntime:
    def __init__(self, memory_engine=None, capability_registry_atlas=None):
        # Registries
        self.capabilities = ProviderCapabilityRegistry()
        self.models = ModelRegistry(self.capabilities)

        # Provider Management
        self.providers = ProviderManager()
        self.router = ProviderRouter(self.providers, self.capabilities)

        # Context & Prompts
        self.conversations = ConversationService()
        self.context = ContextEngine(memory_engine, capability_registry_atlas, self.conversations)
        self.prompts = PromptEngine()
        self.tools = ToolAdapter()

        # Middleware & Streaming
        self.pipeline = PipelineManager(self.capabilities)
        self.stream_manager = StreamManager()

        # Session & Background Workers
        self.session_initializer = SessionInitializer(self.conversations, memory_engine, capability_registry_atlas)
        self.background_workers = BackgroundWorkerPool()

    async def initialize(self):
        await self.background_workers.start()
        logger.info("LLM Runtime Core initialized successfully.")

    async def shutdown(self):
        await self.background_workers.stop()

    async def generate_response(
        self,
        user_message: str,
        ctx: Optional[ExecutionContext] = None,
        tools: Optional[List[ToolDefinition]] = None
    ) -> LLMResponse:
        exec_ctx = ctx or ExecutionContext()
        client, target_model = self.router.select_provider_and_model(exec_ctx)

        # 1. Build Context
        raw_msgs = await self.context.build_context(exec_ctx, user_message)

        # 2. Format Prompt Messages
        prompt_msgs = self.prompts.build_prompt_messages(exec_ctx, raw_msgs)

        # 3. Preprocessing Middleware
        processed_msgs = await self.pipeline.run_preprocessors(exec_ctx, prompt_msgs)

        # 4. Call Provider Adapter
        response = await client.chat(
            messages=processed_msgs,
            tools=tools,
            model=target_model,
            temperature=client.profile.temperature,
            max_tokens=client.profile.max_tokens
        )

        # 5. Postprocessing Middleware
        final_response = await self.pipeline.run_postprocessors(exec_ctx, response)

        # 6. Save in conversation service & queue background tasks
        self.conversations.add_message(exec_ctx.conversation_id, "user", user_message)
        self.conversations.add_message(exec_ctx.conversation_id, "assistant", final_response.content)

        return final_response

    async def generate_stream(
        self,
        user_message: str,
        ctx: Optional[ExecutionContext] = None,
        tools: Optional[List[ToolDefinition]] = None
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        exec_ctx = ctx or ExecutionContext()
        client, target_model = self.router.select_provider_and_model(exec_ctx)

        raw_msgs = await self.context.build_context(exec_ctx, user_message)
        prompt_msgs = self.prompts.build_prompt_messages(exec_ctx, raw_msgs)
        processed_msgs = await self.pipeline.run_preprocessors(exec_ctx, prompt_msgs)

        raw_stream = client.stream(
            messages=processed_msgs,
            tools=tools,
            model=target_model
        )

        async for chunk in self.stream_manager.stream_with_cancellation(exec_ctx, raw_stream):
            yield chunk
