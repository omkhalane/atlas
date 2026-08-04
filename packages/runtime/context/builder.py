import time
import os
from typing import List, Dict, Any
from runtime.kernel.state_manager import StateManager
from runtime.kernel.task import ExecutionTask
from runtime.intelligence.memory import MemoryEngine

class ContextBuilder:
    def __init__(self, state_manager: StateManager, memory_engine: MemoryEngine):
        self.state = state_manager
        self.memory = memory_engine
        
    def _scan_workspace(self, cwd: str) -> str:
        """Lightweight heuristic to detect project type."""
        markers = []
        if os.path.exists(os.path.join(cwd, "package.json")):
            markers.append("Node.js / Javascript / TypeScript project")
        if os.path.exists(os.path.join(cwd, "requirements.txt")) or os.path.exists(os.path.join(cwd, "pyproject.toml")):
            markers.append("Python project")
        if os.path.exists(os.path.join(cwd, "go.mod")):
            markers.append("Go project")
        if os.path.exists(os.path.join(cwd, ".git")):
            markers.append("Git Repository")
            
        return ", ".join(markers) if markers else "Generic Directory"

    def build_context(self, task: ExecutionTask, available_capabilities: List[Dict[str, Any]]) -> str:
        """
        Builds a concise context payload for the Planner LLM.
        """
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        cwd = os.getcwd()
        workspace_type = self._scan_workspace(cwd)
        
        # Load long-term memory
        memory_str = self.memory.get_context_summary()
        
        # Format capabilities cleanly
        caps_str = "\n".join([
            f"- {c['id']}: {', '.join(c.get('actions', []))} "
            f"({c.get('description', 'No description')})"
            for c in available_capabilities
        ])
        
        # Recent tasks context (to provide continuity)
        recent_tasks = list(self.state.tasks.values())[-3:] 
        recent_str = "\n".join([
            f"- Task: {t.goal} | Status: {t.status.value}" for t in recent_tasks if t.id != task.id
        ])
        
        context_prompt = f"""
CURRENT ENVIRONMENT:
Time: {current_time}
Working Directory: {cwd}
Workspace Type: {workspace_type}

LONG TERM MEMORY (Strict Rules & Facts):
{memory_str if memory_str else "No explicit memory set."}

AVAILABLE CAPABILITIES:
{caps_str}

RECENT HISTORY:
{recent_str if recent_str else "No recent tasks."}

USER REQUEST:
{task.goal}
"""
        return context_prompt.strip()
