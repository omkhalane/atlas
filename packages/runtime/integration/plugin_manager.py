import os
import json
from typing import Dict, List, Optional
from pydantic import ValidationError
from .manifest_schema import ManifestSchema
from .capability_registry import registry, RegisteredCapability

class PluginManager:
    def __init__(self, plugins_dir: str = "packages/runtime/integration/catalog/plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, ManifestSchema] = {}
        self.active_plugins: Dict[str, bool] = {}

    def load_all(self):
        if not os.path.exists(self.plugins_dir):
            return
        for fname in os.listdir(self.plugins_dir):
            if fname.endswith(".json"):
                self.load_plugin(os.path.join(self.plugins_dir, fname))

    def load_plugin(self, path: str) -> Optional[ManifestSchema]:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            manifest = ManifestSchema(**data)
            self.plugins[manifest.id] = manifest
            
            # Default state: active if built-in
            # (In a real system, you'd check a user settings file to see if it's disabled)
            self.active_plugins[manifest.id] = True
            
            # Register capabilities
            for cap in manifest.capabilities:
                registry.register(RegisteredCapability(
                    capability_id=cap.id,
                    provider_id=manifest.id,
                    source_type=manifest.type,
                    permissions=cap.permissions,
                    status="available"
                ))
            return manifest
        except Exception as e:
            print(f"Failed to load plugin {path}: {e}")
            return None

    def enable(self, plugin_id: str):
        self.active_plugins[plugin_id] = True

    def disable(self, plugin_id: str):
        self.active_plugins[plugin_id] = False

    def get_plugin(self, plugin_id: str) -> Optional[ManifestSchema]:
        return self.plugins.get(plugin_id)

    def get_all(self) -> List[ManifestSchema]:
        return list(self.plugins.values())

manager = PluginManager()
