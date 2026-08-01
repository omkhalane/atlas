from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class FakeFilesystemPort(AdapterPort):
    def __init__(self):
        self.files = {}

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        op = request.parameters.get("operation")
        path = request.parameters.get("path")
        
        if op == "read":
            if path in self.files:
                return CapabilityResult(success=True, data={"content": self.files[path]})
            return CapabilityResult(success=False, error="File not found")
        elif op == "write":
            self.files[path] = request.parameters.get("content", "")
            return CapabilityResult(success=True)
            
        return CapabilityResult(success=False, error="Unknown operation")

class FakeProcessPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        command = request.parameters.get("command")
        if command == "echo test":
            return CapabilityResult(success=True, data={"stdout": "test\n", "stderr": ""})
        return CapabilityResult(success=False, error="Command failed")
