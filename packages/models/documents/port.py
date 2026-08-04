from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult
import os

class DocumentPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        doc_path = request.parameters.get("doc_path")
        if not doc_path:
            return CapabilityResult(success=False, error="doc_path required")
        if not os.path.exists(doc_path):
            return CapabilityResult(success=False, error=f"File not found: {doc_path}")
            
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()
            return CapabilityResult(success=True, data={"text": content})
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
