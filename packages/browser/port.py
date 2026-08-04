import os
import time
import socket
import subprocess
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult

class BrowserPort(AdapterPort):
    def __init__(self):
        super().__init__()
        self.atlas_browser_executable = os.path.join(
            os.path.dirname(__file__), "atlas-browser", "atlas-browser"
        )

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        script = request.parameters.get("script")
        if not script:
            return CapabilityResult(success=False, error="The 'script' parameter is required to run the atlas-browser.")

        try:
            # We no longer launch an isolated browser. We use browser-harness to connect to the system browser.
            
            # Execute the script via atlas-browser
            proc = subprocess.run(
                [self.atlas_browser_executable],
                input=script,
                capture_output=True,
                text=True
            )
            
            if proc.returncode == 0:
                return CapabilityResult(
                    success=True, 
                    data={"output": proc.stdout}
                )
            else:
                return CapabilityResult(
                    success=False, 
                    error=proc.stderr or proc.stdout
                )
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
