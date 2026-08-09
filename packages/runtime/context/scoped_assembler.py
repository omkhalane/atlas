"""
ScopedContextAssembler — composes existing memory/conversation/state
sources into a bounded context snapshot for the planner.

Import namespace: `runtime.context.scoped_assembler`

Sources (ALL existing — nothing invented):
  1. MemoryEngine.get_context_summary()     — procedural rules + facts
  2. ConversationManager.get_context()      — recent message history
  3. MemoryEngine.search_similar()          — semantic retrieval (optional)
  4. StateManager.tasks                     — recent task history

Scoped by conversation_id — one conversation cannot read another's messages.
Stateless + idempotent — assembly never mutates authoritative state.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.intelligence.memory import MemoryEngine
    from runtime.kernel.state_manager import StateManager
    from runtime.session.conversation import ConversationManager

logger = logging.getLogger("atlas.context_assembler")

DEFAULT_CHAR_BUDGET = 12_000


@dataclass
class AssembledContext:
    conversation_id: str
    execution_id: str
    agent_id: str
    system_rules: str = ""
    recent_messages: List[Dict[str, str]] = field(default_factory=list)
    recent_tasks: str = ""
    semantic_snippets: str = ""
    char_budget_used: int = 0
    truncated: bool = False

    def as_prompt_string(self) -> str:
        parts = []
        if self.system_rules:
            parts.append(f"LONG TERM MEMORY:\n{self.system_rules}")
        if self.recent_messages:
            formatted = "\n".join(
                f"{m.get('role', 'user').upper()}: {m.get('content', '')}"
                for m in self.recent_messages
            )
            parts.append(f"CONVERSATION HISTORY:\n{formatted}")
        if self.semantic_snippets:
            parts.append(f"RELEVANT MEMORY:\n{self.semantic_snippets}")
        if self.recent_tasks:
            parts.append(f"RECENT HISTORY:\n{self.recent_tasks}")
        if self.truncated:
            parts.append("[Context truncated to fit budget]")
        return "\n\n".join(parts)


class ScopedContextAssembler:
    """Stateless; one shared instance per kernel."""

    def __init__(
        self,
        memory: "MemoryEngine",
        conversations: "ConversationManager",
        state: "StateManager",
        char_budget: int = DEFAULT_CHAR_BUDGET,
    ) -> None:
        self._memory = memory
        self._conversations = conversations
        self._state = state
        self._char_budget = char_budget

    def assemble(
        self,
        execution_id: str,
        conversation_id: str,
        agent_id: str = "",
        query: Optional[str] = None,
        message_limit: int = 10,
        task_limit: int = 3,
    ) -> AssembledContext:
        """
        Build a bounded context snapshot. Never raises — degrades gracefully.
        Uses conversation_id to scope message history; cannot access other sessions.
        """
        ctx = AssembledContext(
            conversation_id=conversation_id,
            execution_id=execution_id,
            agent_id=agent_id,
        )
        budget = self._char_budget

        # 1. Procedural rules + facts
        try:
            rules = self._memory.get_context_summary()
            if rules:
                if len(rules) <= budget:
                    ctx.system_rules = rules
                    budget -= len(rules)
                else:
                    ctx.system_rules = rules[:budget]
                    ctx.truncated = True
                    budget = 0
        except Exception as exc:
            logger.warning(f"ScopedContextAssembler: memory rules unavailable: {exc}")

        if budget <= 0:
            ctx.truncated = True
            ctx.char_budget_used = self._char_budget
            return ctx

        # 2. Conversation history (scoped — can only read this conversation)
        try:
            messages = self._conversations.get_context(conversation_id, limit=message_limit)
            if messages:
                msg_str = "\n".join(
                    f"{m.get('role', 'user').upper()}: {m.get('content', '')}"
                    for m in messages
                )
                if len(msg_str) <= budget:
                    ctx.recent_messages = messages
                    budget -= len(msg_str)
                else:
                    # Fit as many recent messages as possible
                    fitting: List[Dict[str, str]] = []
                    used = 0
                    for m in reversed(messages):
                        line = f"{m.get('role', 'user').upper()}: {m.get('content', '')}"
                        if used + len(line) > budget:
                            ctx.truncated = True
                            break
                        fitting.insert(0, m)
                        used += len(line)
                    ctx.recent_messages = fitting
                    budget -= used
        except Exception as exc:
            logger.warning(f"ScopedContextAssembler: conversation unavailable: {exc}")

        # 3. Semantic retrieval (optional, Ollama-backed)
        if query and budget > 0:
            try:
                hits = self._memory.search_similar(query, top_k=3, threshold=0.65)
                snippets = "\n".join(h.get("text", "") for h in hits if h.get("text"))
                if snippets:
                    if len(snippets) <= budget:
                        ctx.semantic_snippets = snippets
                        budget -= len(snippets)
                    else:
                        ctx.semantic_snippets = snippets[:budget]
                        ctx.truncated = True
                        budget = 0
            except Exception as exc:
                logger.debug(f"ScopedContextAssembler: semantic search unavailable: {exc}")

        # 4. Recent task history
        if budget > 0:
            try:
                recent = list(self._state.tasks.values())[-task_limit:]
                lines = [f"- {t.goal} | {t.status.value}" for t in recent]
                task_str = "\n".join(lines)
                if task_str:
                    if len(task_str) <= budget:
                        ctx.recent_tasks = task_str
                        budget -= len(task_str)
                    else:
                        ctx.recent_tasks = task_str[:budget]
                        ctx.truncated = True
            except Exception as exc:
                logger.debug(f"ScopedContextAssembler: task history unavailable: {exc}")

        ctx.char_budget_used = self._char_budget - budget
        return ctx
