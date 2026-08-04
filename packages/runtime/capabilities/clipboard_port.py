import subprocess
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult

class ClipboardPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        action = request.parameters.get("action")
        
        if action == "read":
            try:
                proc = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True)
                if proc.returncode == 0:
                    return CapabilityResult(success=True, data={"clipboard": proc.stdout})
                else:
                    return CapabilityResult(success=False, error=proc.stderr)
            except Exception as e:
                return CapabilityResult(success=False, error=str(e))
                
        elif action == "write":
            content = request.parameters.get("content", "")
            try:
                proc = subprocess.run(["xclip", "-selection", "clipboard", "-i"], input=content, text=True, capture_output=True)
                if proc.returncode == 0:
                    return CapabilityResult(success=True, data={"status": "copied"})
                else:
                    return CapabilityResult(success=False, error=proc.stderr)
            except Exception as e:
                return CapabilityResult(success=False, error=str(e))
                
        return CapabilityResult(success=False, error=f"Unknown action {action}")
