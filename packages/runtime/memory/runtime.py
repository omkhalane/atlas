"""
Memory Runtime — Independent Memory Subsystem Container
"""
from runtime.memory.episodic import EpisodicMemory
from runtime.memory.semantic import SemanticMemory
from runtime.memory.workspace import WorkspaceMemory
from runtime.memory.knowledge import KnowledgeMemory


class MemoryRuntime:
    def __init__(self):
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.workspace = WorkspaceMemory()
        self.knowledge = KnowledgeMemory()

    def get_summary(self) -> str:
        sem_entries = self.semantic.search("", top_k=5)
        if not sem_entries:
            return ""
        return "\n".join([f"- {e['text']}" for e in sem_entries])
