from atlas.core.contracts import UserIntent, CapabilityRequest, CapabilityResult, Plan, Step
from atlas.core.capabilities.manifest import CapabilityManifest

def test_user_intent_creation():
    intent = UserIntent(text="list files", source="cli")
    assert intent.text == "list files"
    assert intent.source == "cli"

def test_capability_request():
    req = CapabilityRequest(id="fs_read", parameters={"path": "/tmp/test.txt"})
    assert req.id == "fs_read"
    assert req.parameters["path"] == "/tmp/test.txt"

def test_capability_manifest():
    manifest = CapabilityManifest(
        id="fs_read",
        description="Reads a file",
        version="1.0.0",
        parameters=[]
    )
    assert manifest.id == "fs_read"
    assert manifest.description == "Reads a file"
