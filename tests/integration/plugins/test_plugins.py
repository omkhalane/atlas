import os
from atlas.core.capabilities.engine import CapabilityEngine
from atlas.core.plugins.manager import PluginManager
from atlas.core.contracts import CapabilityRequest

def test_plugin_loading():
    capability_engine = CapabilityEngine()
    manager = PluginManager(capability_engine)

    plugin_path = os.path.join(os.path.dirname(__file__), "../../../plugins/examples/hello_plugin.py")
    plugin_path = os.path.abspath(plugin_path)

    success = manager.load_plugin_from_file(plugin_path, "hello_plugin")
    assert success is True

    manifest = capability_engine.get_manifest("hello_world")
    assert manifest is not None
    assert manifest.description == "Says hello"

    res = capability_engine.execute(CapabilityRequest(id="hello_world", parameters={"name": "Atlas"}))
    assert res.success
    assert res.data["message"] == "Hello, Atlas!"
