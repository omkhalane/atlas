import subprocess
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult

class ProcessPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        command = request.parameters.get("command")
        timeout = request.parameters.get("timeout", 10)
        
        if not command:
            return CapabilityResult(success=False, error="Command parameter required")

        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return CapabilityResult(
                success=(proc.returncode == 0),
                data={"stdout": proc.stdout, "stderr": proc.stderr, "exit_code": proc.returncode}
            )
        except subprocess.TimeoutExpired:
            return CapabilityResult(success=False, error=f"Command timed out after {timeout} seconds")
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
