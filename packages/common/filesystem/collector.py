import os
from typing import Dict, Any

class FilesystemCollector:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def collect(self) -> Dict[str, Any]:
        state = {"files": [], "directories": []}
        try:
            for root, dirs, files in os.walk(self.root_dir):
                if '.git' in dirs:
                    dirs.remove('.git')
                
                rel_root = os.path.relpath(root, self.root_dir)
                if rel_root == ".":
                    rel_root = ""
                    
                for d in dirs:
                    state["directories"].append(os.path.join(rel_root, d) if rel_root else d)
                for f in files:
                    state["files"].append(os.path.join(rel_root, f) if rel_root else f)
        except Exception as e:
            state["error"] = str(e)
            
        return state
