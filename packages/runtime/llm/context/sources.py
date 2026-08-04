"""
Composable Context Sources
Each ContextSource gathers a slice of state independently.
"""
import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from runtime.llm.contracts import ExecutionContext, LLMMessage


class BaseContextSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """Higher integer = higher priority when trimming context."""
        pass

    @abstractmethod
    async def get_messages(self, ctx: ExecutionContext) -> List[LLMMessage]:
        pass


class SystemSource(BaseContextSource):
    @property
    def name(self) -> str:
        return "system"

    @property
    def priority(self) -> int:
        return 100  # Never prune system prompt if possible

    async def get_messages(self, ctx: ExecutionContext) -> List[LLMMessage]:
        sys_text = (
            "You are Atlas, an enterprise-grade autonomous AI coding & execution assistant.\n"
            f"Working Directory: {ctx.workspace_path or os.getcwd()}\n"
            f"Current Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return [LLMMessage(role="system", content=sys_text)]


class ConversationSource(BaseContextSource):
    def __init__(self, conversation_service=None):
        self.conv_service = conversation_service

    @property
    def name(self) -> str:
        return "conversation"

    @property
    def priority(self) -> int:
        return 90

    async def get_messages(self, ctx: ExecutionContext) -> List[LLMMessage]:
        if not self.conv_service:
            return []
        recent = self.conv_service.get_recent_messages(ctx.conversation_id, limit=10)
        return [LLMMessage(role=m["role"], content=m["content"]) for m in recent]


class MemorySource(BaseContextSource):
    def __init__(self, memory_engine=None):
        self.memory = memory_engine

    @property
    def name(self) -> str:
        return "memory"

    @property
    def priority(self) -> int:
        return 70

    async def get_messages(self, ctx: ExecutionContext) -> List[LLMMessage]:
        if not self.memory:
            return []
        summary = self.memory.get_context_summary()
        if not summary:
            return []
        return [LLMMessage(role="system", content=f"LONG-TERM USER MEMORY:\n{summary}")]


class WorkspaceSource(BaseContextSource):
    @property
    def name(self) -> str:
        return "workspace"

    @property
    def priority(self) -> int:
        return 60

    async def get_messages(self, ctx: ExecutionContext) -> List[LLMMessage]:
        cwd = ctx.workspace_path or os.getcwd()
        markers = []
        if os.path.exists(os.path.join(cwd, "package.json")):
            markers.append("Node.js/TypeScript")
        if os.path.exists(os.path.join(cwd, "pyproject.toml")) or os.path.exists(os.path.join(cwd, "requirements.txt")):
            markers.append("Python")
        if os.path.exists(os.path.join(cwd, ".git")):
            markers.append("Git Repo")

        info = f"WORKSPACE CONTEXT: {cwd} ({', '.join(markers) if markers else 'Generic Project'})"
        return [LLMMessage(role="system", content=info)]


class CapabilitySource(BaseContextSource):
    def __init__(self, registry=None):
        self.registry = registry

    @property
    def name(self) -> str:
        return "capabilities"

    @property
    def priority(self) -> int:
        return 80

    async def get_messages(self, ctx: ExecutionContext) -> List[LLMMessage]:
        if not self.registry:
            return []
        caps = self.registry.get_capabilities_manifest()
        caps_str = "\n".join([
            f"- {c['id']}: {', '.join(c.get('actions', []))} ({c.get('description', '')})"
            for c in caps
        ])
        return [LLMMessage(role="system", content=f"AVAILABLE ATLAS CAPABILITIES:\n{caps_str}")]
