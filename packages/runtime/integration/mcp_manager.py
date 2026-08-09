import os
import json
from typing import Dict, List, Optional
from pydantic import ValidationError
from .manifest_schema import ManifestSchema
from .capability_registry import registry, RegisteredCapability

class MCPManager:
    def __init__(self, catalog_file: str = "packages/runtime/integration/catalog/mcp_registry.json"):
        self.catalog_file = catalog_file
        self.installed_mcps: Dict[str, ManifestSchema] = {}
        self.available_mcps: Dict[str, ManifestSchema] = {}
        self.connection_status: Dict[str, str] = {} # "connected", "disconnected", "error"

    def load_catalog(self):
        if not os.path.exists(self.catalog_file):
            return
        try:
            with open(self.catalog_file, 'r') as f:
                catalog = json.load(f)
                for entry in catalog:
                    try:
                        manifest = ManifestSchema(**entry)
                        self.available_mcps[manifest.id] = manifest
                    except ValidationError as e:
                        print(f"Validation error for MCP catalog entry {entry.get('id')}: {e}")
        except Exception as e:
            print(f"Failed to load MCP catalog: {e}")

    def get_available(self) -> List[ManifestSchema]:
        return list(self.available_mcps.values())

    def get_installed(self) -> List[ManifestSchema]:
        return list(self.installed_mcps.values())

    def install(self, mcp_id: str):
        if mcp_id not in self.available_mcps:
            raise ValueError(f"MCP {mcp_id} not found in catalog")
        
        manifest = self.available_mcps[mcp_id]
        self.installed_mcps[mcp_id] = manifest
        self.connection_status[mcp_id] = "disconnected"
        
        # Register capabilities
        for cap in manifest.capabilities:
            registry.register(RegisteredCapability(
                capability_id=cap.id,
                provider_id=manifest.id,
                source_type=manifest.type,
                permissions=cap.permissions,
                status="available"
            ))

    def connect(self, mcp_id: str):
        if mcp_id in self.installed_mcps:
            self.connection_status[mcp_id] = "connected"

    def disconnect(self, mcp_id: str):
        if mcp_id in self.installed_mcps:
            self.connection_status[mcp_id] = "disconnected"

    def uninstall(self, mcp_id: str):
        if mcp_id in self.installed_mcps:
            del self.installed_mcps[mcp_id]
            del self.connection_status[mcp_id]
            registry.unregister_provider(mcp_id)

manager = MCPManager()
