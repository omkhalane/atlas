import subprocess
from typing import Dict, Any

class GitCollector:
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir

    def collect(self) -> Dict[str, Any]:
        state = {"branch": None, "commit": None, "is_dirty": False, "error": None}
        try:
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.repo_dir, capture_output=True, check=True)
            
            branch_proc = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.repo_dir, capture_output=True, text=True)
            if branch_proc.returncode == 0:
                state["branch"] = branch_proc.stdout.strip()
                
            commit_proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo_dir, capture_output=True, text=True)
            if commit_proc.returncode == 0:
                state["commit"] = commit_proc.stdout.strip()
                
            status_proc = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_dir, capture_output=True, text=True)
            if status_proc.returncode == 0:
                state["is_dirty"] = len(status_proc.stdout.strip()) > 0
                
        except subprocess.CalledProcessError:
            state["error"] = "Not a git repository or git error."
        except Exception as e:
            state["error"] = str(e)
            
        return state
