import subprocess
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult

class MacOSClipboardPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        op = request.parameters.get("operation")
        try:
            if op == "read":
                proc = subprocess.run(["pbpaste"], capture_output=True, text=True)
                return CapabilityResult(success=(proc.returncode == 0), data={"content": proc.stdout})
            elif op == "write":
                content = request.parameters.get("content", "")
                proc = subprocess.run(["pbcopy"], input=content, capture_output=True, text=True)
                return CapabilityResult(success=(proc.returncode == 0))
            else:
                return CapabilityResult(success=False, error=f"Unknown operation: {op}")
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
