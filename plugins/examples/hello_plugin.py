from typing import Dict
from atlas.core.plugins.base import Plugin
from atlas.core.contracts.plugin import PluginManifest
from atlas.core.capabilities.manifest import CapabilityManifest
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class HelloAdapter(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        name = request.parameters.get("name", "World")
        return CapabilityResult(success=True, data={"message": f"Hello, {name}!"})

class HelloPlugin(Plugin):
    def get_manifest(self) -> PluginManifest:
        return PluginManifest(
            id="hello-plugin",
            name="Hello Plugin",
            version="1.0.0",
            description="A simple example plugin",
            capabilities=[
                CapabilityManifest(
                    id="hello_world",
                    description="Says hello",
                    version="1.0.0",
                    parameters=[],
                    required_permissions=[]
                )
            ]
        )

    def get_adapters(self) -> Dict[str, AdapterPort]:
        return {
            "hello_world": HelloAdapter()
        }
