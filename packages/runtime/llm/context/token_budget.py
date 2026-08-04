"""
Token Budget Manager
Calculates token budgets per source and intelligently prunes low-priority sources.
"""
from typing import List
from runtime.llm.contracts import LLMMessage
from runtime.llm.context.sources import BaseContextSource


class TokenBudgetManager:
    def __init__(self, max_context_tokens: int = 128000, max_output_tokens: int = 4096):
        self.max_context_tokens = max_context_tokens
        self.max_output_tokens = max_output_tokens

    def estimate_tokens(self, text: str) -> int:
        """Lightweight token estimator (~4 chars per token)."""
        return max(1, len(text) // 4)

    def count_message_tokens(self, messages: List[LLMMessage]) -> int:
        return sum(self.estimate_tokens(m.content) for m in messages)

    def fit_to_budget(self, sources_with_messages: List[tuple[BaseContextSource, List[LLMMessage]]]) -> List[LLMMessage]:
        # Target token ceiling for input prompt
        input_budget = self.max_context_tokens - self.max_output_tokens - 1000

        # Sort sources by priority descending (highest priority kept first)
        sorted_sources = sorted(sources_with_messages, key=lambda x: x[0].priority, reverse=True)

        final_messages: List[LLMMessage] = []
        current_tokens = 0

        for source, msgs in sorted_sources:
            src_tokens = self.count_message_tokens(msgs)
            if current_tokens + src_tokens <= input_budget:
                final_messages.extend(msgs)
                current_tokens += src_tokens
            else:
                # Partial trimming: keep what fits
                for m in msgs:
                    m_tok = self.estimate_tokens(m.content)
                    if current_tokens + m_tok <= input_budget:
                        final_messages.append(m)
                        current_tokens += m_tok

        return final_messages
