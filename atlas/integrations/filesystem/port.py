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
                data={"path": abs_path, "action": action, "content": content}
            )

        rollback_dir = "/code/ATLAS/.rollback"
        os.makedirs(rollback_dir, exist_ok=True)
        import uuid
        import shutil
            
        try:
            if action == "write_file":
                tx_id = str(uuid.uuid4())
                if os.path.exists(abs_path):
                    shutil.copy2(abs_path, os.path.join(rollback_dir, f"{tx_id}_backup"))
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "w") as f:
                    f.write(content)
                return CapabilityResult(success=True, data={"path": abs_path, "tx_id": tx_id})
            elif action == "append_file":
                tx_id = str(uuid.uuid4())
                if os.path.exists(abs_path):
                    shutil.copy2(abs_path, os.path.join(rollback_dir, f"{tx_id}_backup"))
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "a") as f:
                    f.write(content)
                return CapabilityResult(success=True, data={"path": abs_path, "tx_id": tx_id})
            elif action == "delete_file":
                tx_id = str(uuid.uuid4())
                import glob
                paths = glob.glob(abs_path) if '*' in abs_path else [abs_path]
                deleted = []
                for idx, p in enumerate(paths):
                    if os.path.isfile(p):
                        shutil.copy2(p, os.path.join(rollback_dir, f"{tx_id}_{idx}_backup"))
                        os.remove(p)
                        deleted.append(p)
                return CapabilityResult(success=True, data={"paths_deleted": deleted, "tx_id": tx_id})
            elif action == "undo":
                tx_id = request.parameters.get("tx_id")
                if not tx_id:
                    return CapabilityResult(success=False, error="tx_id is required for undo")
                import glob
                backups = glob.glob(os.path.join(rollback_dir, f"{tx_id}*"))
                if not backups:
                    return CapabilityResult(success=False, error="No backups found for transaction")
                # Very basic restore mechanism. Real world would track exact target paths.
                # For this MVP, we simply move it back to the original absolute path if it was 1 file.
                # Since we don't have a manifest, we assume the original path is `abs_path`.
                for backup in backups:
                    shutil.copy2(backup, abs_path)
                return CapabilityResult(success=True, data={"restored_path": abs_path})
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
