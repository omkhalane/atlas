from typing import Dict, Optional, TYPE_CHECKING
from atlas.core.contracts import CapabilityRequest, CapabilityResult
from atlas.core.capabilities.manifest import CapabilityManifest

if TYPE_CHECKING:
    from atlas.adapters.ports import AdapterPort

class CapabilityEngine:
    def __init__(self):
        self._adapters: Dict[str, 'AdapterPort'] = {}
        self._manifests: Dict[str, CapabilityManifest] = {}

    def register(self, manifest: CapabilityManifest, adapter: 'AdapterPort'):
        self._manifests[manifest.id] = manifest
        self._adapters[manifest.id] = adapter

    def get_manifest(self, capability_id: str) -> Optional[CapabilityManifest]:
        return self._manifests.get(capability_id)

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        adapter = self._adapters.get(request.id)
        if not adapter:
            return CapabilityResult(success=False, error=f"Capability '{request.id}' not found.")
        
        try:
            return adapter.execute(request)
        except Exception as e:
            return CapabilityResult(success=False, error=f"Adapter execution failed: {str(e)}")
