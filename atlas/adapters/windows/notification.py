import subprocess
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class WindowsNotificationPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        message = request.parameters.get("message")
        title = request.parameters.get("title", "Atlas")
        if not message:
            return CapabilityResult(success=False, error="Message parameter required")
        try:
            proc = subprocess.run(["powershell", "-command", f"Write-Output 'Notification: {title} - {message}'"], capture_output=True, text=True)
            return CapabilityResult(success=(proc.returncode == 0))
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
