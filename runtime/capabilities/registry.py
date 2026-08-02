from typing import Dict, Any, List
import logging
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult
from browser.port import BrowserPort
from filesystem.port import FilesystemPort
from terminal.port import CommandPort
from models.media.port import MediaPort
from plugins.mcp_client import MCPAdapter, MCPClient

from runtime.kernel.state_manager import StateManager
from runtime.capabilities.search_port import SearchPort
from runtime.capabilities.clipboard_port import ClipboardPort
from runtime.capabilities.memory_port import MemoryPort
from runtime.intelligence.memory import MemoryEngine

logger = logging.getLogger("atlas.capabilities")

class CapabilityRegistry:
    def __init__(self, state_manager: StateManager, memory_engine: MemoryEngine):
        self._capabilities: Dict[str, AdapterPort] = {}
        self._mcp_clients: List[MCPClient] = []
        
        # Register core runtimes
        self.register("browser", BrowserPort())
        self.register("filesystem", FilesystemPort())
        self.register("command", CommandPort())
        self.register("media", MediaPort())
        self.register("search", SearchPort(state_manager))
        self.register("clipboard", ClipboardPort())
        self.register("memory", MemoryPort(memory_engine))

    def register(self, capability_id: str, port: AdapterPort):
        self._capabilities[capability_id] = port
        
    def register_mcp(self, name: str, client: MCPClient):
        self._mcp_clients.append(client)
        self.register(f"mcp_{name}", MCPAdapter(client))

    def get_capabilities_manifest(self) -> List[Dict[str, Any]]:
        manifests = [
            {"id": "media", "actions": ["start_recording", "stop_recording", "take_screenshot"]},
            {"id": "filesystem", "actions": ["write_file", "append_file", "delete_file", "list_files", "undo"], "description": "Local filesystem operations"},
            {"id": "command", "actions": ["run"], "description": "Execute bash commands"},
            {"id": "browser", "actions": ["run"], "description": "Control browser using browser-harness script payload"},
            {"id": "search", "actions": ["query"], "description": "Unified search across filesystem and tasks"},
            {"id": "clipboard", "actions": ["read", "write"], "description": "Read or write to the system clipboard"},
            {"id": "memory", "actions": ["store", "get", "get_category"], "description": "Read or write to long-term memory"}
        ]
        
        for mcp_id, port in self._capabilities.items():
            if mcp_id.startswith("mcp_"):
                # Port is MCPAdapter
                adapter: MCPAdapter = port
                tools = adapter.mcp_client.get_tools()
                actions = [t["name"] for t in tools] if tools else ["*"]
                manifests.append({"id": mcp_id, "actions": actions, "description": f"MCP Plugin: {mcp_id}"})
                
        return manifests

    async def execute(self, capability_id: str, request: CapabilityRequest) -> CapabilityResult:
        if capability_id not in self._capabilities:
            return CapabilityResult(success=False, error=f"Unknown capability: {capability_id}")
            
        port = self._capabilities[capability_id]
        
        # execute is sync in AdapterPort but we run it in thread to avoid blocking if needed,
        # or we just call it.
        # Actually port.execute() blocks currently, let's just call it. 
        # (A production system might wrap it in asyncio.to_thread)
        import asyncio
        try:
            return await asyncio.to_thread(port.execute, request)
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
