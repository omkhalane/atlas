import os
import subprocess
from typing import List, Dict, Any
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult
from runtime.kernel.state_manager import StateManager

class SearchPort(AdapterPort):
    def __init__(self, state_manager: StateManager):
        super().__init__()
        self.state = state_manager

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        query = request.parameters.get("query")
        domains = request.parameters.get("domains", ["filesystem", "tasks"])
        
        if not query:
            return CapabilityResult(success=False, error="Query is required for search.")

        results = {}

        if "filesystem" in domains:
            try:
                # Ripgrep search
                proc = subprocess.run(
                    ["rg", "-i", query, "/code/ATLAS"],
                    capture_output=True,
                    text=True
                )
                if proc.returncode in [0, 1]:  # 1 means no match
                    results["filesystem"] = proc.stdout.split("\n")[:50] # limit to 50 lines
                else:
                    results["filesystem"] = f"Error: {proc.stderr}"
            except Exception as e:
                results["filesystem"] = f"Error: {str(e)}"

        if "tasks" in domains:
            # Search active task memory (history)
            task_matches = []
            for t in self.state.tasks.values():
                if query.lower() in t.goal.lower():
                    task_matches.append({"task_id": t.id, "goal": t.goal, "status": t.status.value})
            results["tasks"] = task_matches

        return CapabilityResult(success=True, data=results)
