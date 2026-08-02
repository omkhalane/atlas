import os
from typing import Dict, Any
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class FilesystemPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        action = request.parameters.get("action")
        path = request.parameters.get("path")
        content = request.parameters.get("content", "")
        approved = request.parameters.get("approved", False)
        
        if not path:
            return CapabilityResult(success=False, error="path is required")
            
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        # Security Sandbox Check
        if not abs_path.startswith("/code/ATLAS") and not approved:
            return CapabilityResult(
                success=False, 
                error=f"Security Halt: Attempted to access {abs_path} which is outside the /code/ATLAS sandbox. Human approval required.",
                requires_human=True,
                data={"path": abs_path, "action": action, "content": content}
            )
            
        try:
            if action == "write_file":
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "w") as f:
                    f.write(content)
                return CapabilityResult(success=True, data={"path": abs_path})
            elif action == "append_file":
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "a") as f:
                    f.write(content)
                return CapabilityResult(success=True, data={"path": abs_path})
            elif action == "delete_file":
                import glob
                paths = glob.glob(abs_path) if '*' in abs_path else [abs_path]
                deleted = []
                for p in paths:
                    if os.path.isfile(p):
                        os.remove(p)
                        deleted.append(p)
                return CapabilityResult(success=True, data={"paths_deleted": deleted})
            elif action == "list_files":
                import glob
                paths = glob.glob(abs_path) if '*' in abs_path else [abs_path]
                files = []
                for p in paths:
                    if os.path.isdir(p):
                        files.extend([os.path.join(p, f) for f in os.listdir(p)])
                    else:
                        files.append(p)
                return CapabilityResult(success=True, data={"files": files})
            else:
                return CapabilityResult(success=False, error=f"Unknown filesystem action: {action}")
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
