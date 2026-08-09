"""
Capability Registry Adapter
Adapts the runtime CapabilityRegistry (which uses CapabilityRequest) 
to the core IToolExecutor interface.
"""
from core.python.contracts.tool import IToolExecutor, ToolResult
from runtime.contracts import CapabilityRequest
from runtime.capabilities.registry import CapabilityRegistry

class RegistryToolWrapper(IToolExecutor):
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry
        
    async def execute_tool(self, name: str, arguments: dict) -> ToolResult:
        req = CapabilityRequest(id=name, parameters=arguments)
        res = await self.registry.execute(name, req)
        return ToolResult(
            result=str(res.data) if res.success else "", 
            error=res.error if not res.success else None
        )
