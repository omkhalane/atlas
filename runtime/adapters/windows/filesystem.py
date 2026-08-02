import os
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult

class WindowsFilesystemPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        op = request.parameters.get("operation")
        path = request.parameters.get("path")
        if not path:
            return CapabilityResult(success=False, error="Path parameter required")

        try:
            if op == "read":
                if not os.path.exists(path):
                    return CapabilityResult(success=False, error=f"File not found: {path}")
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return CapabilityResult(success=True, data={"content": content})
            elif op == "write":
                content = request.parameters.get("content", "")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return CapabilityResult(success=True)
            else:
                return CapabilityResult(success=False, error=f"Unknown operation: {op}")
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
