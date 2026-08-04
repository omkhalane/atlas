"""
Workspace Memory — Repository Structure & Environment Memory
"""
import os
from typing import Dict, Any


class WorkspaceMemory:
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get_workspace_info(self, cwd: str) -> Dict[str, Any]:
        if cwd in self._cache:
            return self._cache[cwd]
        info = {
            "path": cwd,
            "has_git": os.path.exists(os.path.join(cwd, ".git")),
            "has_package_json": os.path.exists(os.path.join(cwd, "package.json")),
            "has_pyproject": os.path.exists(os.path.join(cwd, "pyproject.toml"))
        }
        self._cache[cwd] = info
        return info
