import os
import time
import socket
import subprocess
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class BrowserPort(AdapterPort):
    def __init__(self):
        super().__init__()
        self.atlas_browser_executable = os.path.join(
            os.path.dirname(__file__), "atlas-browser", "atlas-browser"
        )
        self.port = 9222

    def _is_port_open(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0

    def _ensure_browser_running(self):
        if self._is_port_open(self.port):
            return

        print(f"[*] Auto-launching Chrome with --remote-debugging-port={self.port}...")
        
        # Determine Chrome executable
        candidates = [
            "google-chrome",
            "google-chrome-stable",
            "chromium",
            "chromium-browser",
            "chrome"
        ]
        
        chrome_bin = None
        for candidate in candidates:
            if subprocess.run(["which", candidate], capture_output=True).returncode == 0:
                chrome_bin = candidate
                break
                
        if not chrome_bin:
            raise RuntimeError("Could not find a valid Chrome/Chromium installation to auto-launch.")
            
        # Launch browser in background
        subprocess.Popen(
            [chrome_bin, f"--remote-debugging-port={self.port}", "--remote-allow-origins=*", "about:blank"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait up to 5 seconds for port to open
        start_time = time.time()
        while time.time() - start_time < 5:
            if self._is_port_open(self.port):
                time.sleep(1) # Give it a brief moment to initialize its CDP server fully
                return
            time.sleep(0.5)
            
        raise RuntimeError("Failed to auto-launch Chrome and connect to debugging port.")

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        script = request.parameters.get("script")
        if not script:
            return CapabilityResult(success=False, error="The 'script' parameter is required to run the atlas-browser.")

        try:
            self._ensure_browser_running()
            
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
