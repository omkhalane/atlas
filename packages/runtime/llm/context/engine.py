"""
Context Engine
Assembles composable ContextSources and applies TokenBudgetManager.
"""
from typing import List, Tuple
from runtime.llm.contracts import ExecutionContext, LLMMessage
from runtime.llm.context.sources import (
    BaseContextSource, SystemSource, MemorySource, WorkspaceSource, CapabilitySource, ConversationSource
)
from runtime.llm.context.token_budget import TokenBudgetManager


class ContextEngine:
    def __init__(self, memory_engine=None, capability_registry=None, conversation_service=None):
        self.sources: List[BaseContextSource] = [
            SystemSource(),
            MemorySource(memory_engine),
            WorkspaceSource(),
            CapabilitySource(capability_registry),
            ConversationSource(conversation_service)
        ]

    def add_source(self, source: BaseContextSource):
        self.sources.append(source)

    async def build_context(self, ctx: ExecutionContext, user_message: str) -> List[LLMMessage]:
        sources_msgs: List[Tuple[BaseContextSource, List[LLMMessage]]] = []
        for src in self.sources:
            try:
                msgs = await src.get_messages(ctx)
                if msgs:
                    sources_msgs.append((src, msgs))
            except Exception:
                pass

        budget_manager = TokenBudgetManager(max_context_tokens=128000, max_output_tokens=4096)
        assembled_msgs = budget_manager.fit_to_budget(sources_msgs)

        # Append user message at the very end
        assembled_msgs.append(LLMMessage(role="user", content=user_message))
        return assembled_msgs
