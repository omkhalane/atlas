import subprocess
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult

class ClipboardPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        op = request.parameters.get("operation")
        
        try:
            if op == "read":
                proc = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True)
                if proc.returncode == 0:
                    return CapabilityResult(success=True, data={"content": proc.stdout})
                else:
                    return CapabilityResult(success=False, error="Failed to read clipboard")
                    
            elif op == "write":
                content = request.parameters.get("content", "")
                proc = subprocess.run(["xclip", "-selection", "clipboard", "-i"], input=content, capture_output=True, text=True)
                if proc.returncode == 0:
                    return CapabilityResult(success=True)
                else:
                    return CapabilityResult(success=False, error="Failed to write clipboard")
                    
            else:
                return CapabilityResult(success=False, error=f"Unknown operation: {op}")
        except FileNotFoundError:
            return CapabilityResult(success=False, error="xclip command not found")
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
