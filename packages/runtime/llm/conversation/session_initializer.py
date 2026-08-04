"""
Session Initializer — Progressive Loading & Prompt Cache Warmup
"""
import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from runtime.llm.contracts import ExecutionContext

logger = logging.getLogger("atlas.llm.session_initializer")


class SessionInitializer:
    def __init__(self, conversation_service=None, memory_engine=None, capability_registry=None):
        self.conv_service = conversation_service
        self.memory = memory_engine
        self.capabilities = capability_registry

    async def initialize_session(
        self,
        ctx: ExecutionContext,
        on_progress: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        stages = [
            ("Loading Conversation State", 10),
            ("Loading Conversation Summary", 30),
            ("Loading Relevant Memories", 50),
            ("Loading Workspace Context", 70),
            ("Loading Atlas Capabilities", 85),
            ("Warming Prompt Cache", 95),
            ("Session Ready", 100)
        ]

        session_context = {}

        for stage, pct in stages:
            if on_progress:
                on_progress(stage, pct)

            if pct == 10 and self.conv_service:
                conv = self.conv_service.get_or_create(ctx.conversation_id)
                session_context["conversation"] = conv

            elif pct == 30 and self.conv_service:
                conv = self.conv_service.get(ctx.conversation_id)
                session_context["summary"] = conv.summary if conv else ""

            elif pct == 50 and self.memory:
                session_context["memories"] = self.memory.get_context_summary()

            elif pct == 85 and self.capabilities:
                session_context["capabilities"] = self.capabilities

            elif pct == 95:
                # Prompt cache warmup simulate/prepare
                await asyncio.sleep(0.01)

        logger.info(f"Session initialized successfully for conversation {ctx.conversation_id}")
        return session_context
