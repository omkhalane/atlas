from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult
from runtime.intelligence.memory import MemoryEngine

class MemoryPort(AdapterPort):
    def __init__(self, memory_engine: MemoryEngine):
        super().__init__()
        self.memory_engine = memory_engine

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        action = request.parameters.get("action")
        
        if action == "store":
            category = request.parameters.get("category", "fact")
            key = request.parameters.get("key")
            value = request.parameters.get("value")
            
            if not key or not value:
                return CapabilityResult(success=False, error="Key and value are required to store memory.")
                
            self.memory_engine.store(category, key, value)
            return CapabilityResult(success=True, data={"status": "stored", "key": key})
            
        elif action == "get":
            key = request.parameters.get("key")
            if not key:
                return CapabilityResult(success=False, error="Key is required to get memory.")
                
            val = self.memory_engine.get(key)
            if val is not None:
                return CapabilityResult(success=True, data={"key": key, "value": val})
            else:
                return CapabilityResult(success=False, error=f"Memory {key} not found.")
                
        elif action == "get_category":
            category = request.parameters.get("category")
            if not category:
                return CapabilityResult(success=False, error="Category is required.")
                
            results = self.memory_engine.get_all_by_category(category)
            return CapabilityResult(success=True, data={"category": category, "results": results})
            
        return CapabilityResult(success=False, error=f"Unknown memory action: {action}")
