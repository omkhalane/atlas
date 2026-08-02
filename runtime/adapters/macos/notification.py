import subprocess
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult

class MacOSNotificationPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        message = request.parameters.get("message")
        title = request.parameters.get("title", "Atlas")
        if not message:
            return CapabilityResult(success=False, error="Message parameter required")
        try:
            script = f'display notification "{message}" with title "{title}"'
            proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            return CapabilityResult(success=(proc.returncode == 0))
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
