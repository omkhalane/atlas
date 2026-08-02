import os
import subprocess
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class CommandPort(AdapterPort):
    def __init__(self, workspace_dir="/code/ATLAS"):
        super().__init__()
        self.workspace_dir = workspace_dir

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        command = request.parameters.get("command")
        if not command:
            return CapabilityResult(success=False, error="command is required")
        background = request.parameters.get("background", False)
            
        try:
            if background:
                proc = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=self.workspace_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return CapabilityResult(
                    success=True,
                    data={"output": f"Job started in background with PID {proc.pid}", "pid": proc.pid}
                )
                
            # We enforce that the command is executed within the workspace
            proc = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=60 # 1 minute timeout
            )
            
            output = proc.stdout.strip()
            err = proc.stderr.strip()
            
            # Combine them for the LLM to observe
            full_output = ""
            if output:
                full_output += f"STDOUT:\n{output}\n"
            if err:
                full_output += f"STDERR:\n{err}\n"
                
            if not full_output:
                full_output = "Command executed successfully with no output."
                
            return CapabilityResult(
                success=(proc.returncode == 0),
                data={"output": full_output, "exit_code": proc.returncode}
            )
            
        except subprocess.TimeoutExpired:
            return CapabilityResult(success=False, error="Command timed out after 60 seconds.")
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
