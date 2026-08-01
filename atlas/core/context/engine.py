from typing import Dict, Any, List, Optional
from atlas.core.contracts import UserIntent, ContextSnapshot
from atlas.core.memory.store import MemoryStore
from atlas.integrations.filesystem.collector import FilesystemCollector
from atlas.integrations.git.collector import GitCollector
from atlas.core.security.filters import SensitivityFilter

class ContextEngine:
    def __init__(self, memory: MemoryStore, fs_collector: FilesystemCollector, git_collector: GitCollector, sensitivity_filter: Optional[SensitivityFilter] = None):
        self.memory = memory
        self.fs_collector = fs_collector
        self.git_collector = git_collector
        self.sensitivity_filter = sensitivity_filter

    def snapshot(self, intent: UserIntent) -> ContextSnapshot:
        facts = self.memory.search(intent.text)
        memory_state = {
            "facts": [{"id": f.id, "content": f.content, "provenance": f.provenance} for f in facts]
        }
        
        project_state = {
            "filesystem": self.fs_collector.collect(),
            "git": self.git_collector.collect()
        }

        if self.sensitivity_filter:
            memory_state = self.sensitivity_filter.filter_dict(memory_state)
            project_state = self.sensitivity_filter.filter_dict(project_state)

        return ContextSnapshot(
            intent=intent,
            state=project_state,
            memory=memory_state
        )
