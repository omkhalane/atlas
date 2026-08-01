import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from atlas.core.capabilities.engine import CapabilityEngine
from atlas.core.security.engine import SecurityEngine
from atlas.core.security.filters import SensitivityFilter
from atlas.core.runtime.validator import Validator
from atlas.core.runtime.verifier import Verifier
from atlas.core.runtime.ledger import SQLiteLedger
from atlas.core.runtime.engine import Runtime
from atlas.core.plugins.manager import PluginManager
from atlas.core.workflows.engine import WorkflowEngine
from atlas.core.workflows.schema import Workflow
from atlas.core.contracts import Step, CapabilityRequest, UserIntent, PolicyDecision
from atlas.core.memory.store import MemoryStore, Fact
from atlas.integrations.filesystem.collector import FilesystemCollector
from atlas.integrations.git.collector import GitCollector
from atlas.core.context.engine import ContextEngine
from atlas.adapters.factory import get_platform_adapters
from atlas.core.capabilities.manifest import CapabilityManifest

def main():
    if os.path.exists("demo_ledger.db"):
        os.remove("demo_ledger.db")
    if os.path.exists("demo_memory.db"):
        os.remove("demo_memory.db")

    print("=== ATLAS End-to-End System Demo ===\n")
    
    print("[*] Initializing Core Engines...")
    cap_engine = CapabilityEngine()
    sec_engine = SecurityEngine()
    sec_engine.authorize = lambda req: PolicyDecision(granted=True, reason="Demo mode")
    
    ledger = SQLiteLedger("demo_ledger.db")
    validator = Validator(cap_engine)
    verifier = Verifier()
    runtime = Runtime(cap_engine, sec_engine, ledger, validator, verifier)
    
    print("[*] Registering Platform Adapters...")
    adapters = get_platform_adapters()
    fs_manifest = CapabilityManifest(id="filesystem", description="FS Ops", version="1.0", parameters=[], required_permissions=[])
    cap_engine.register(fs_manifest, adapters["filesystem"])
    
    print("[*] Loading External Plugin...")
    plugin_mgr = PluginManager(cap_engine)
    plugin_path = os.path.abspath("plugins/examples/hello_plugin.py")
    plugin_mgr.load_plugin_from_file(plugin_path, "hello_plugin")
    print(f"    Available Capabilities: {list(cap_engine._manifests.keys())}")
    
    print("\n[*] Gathering Context & Memory...")
    memory = MemoryStore("demo_memory.db")
    memory.store(Fact(id="f1", content="Demo fact containing secret@example.com", provenance="demo"))
    
    fs_col = FilesystemCollector(".")
    git_col = GitCollector(".")
    s_filter = SensitivityFilter()
    
    ctx_engine = ContextEngine(memory, fs_col, git_col, s_filter)
    snapshot = ctx_engine.snapshot(UserIntent(text="demo fact", source="cli"))
    
    print(f"    Context gathered. Found {len(snapshot.state['filesystem']['files'])} files in project root.")
    print(f"    Filtered Memory Fact: {snapshot.memory['facts'][0]['content']}")
    
    print("\n[*] Executing Workflow...")
    wf_engine = WorkflowEngine(runtime)
    wf = Workflow(
        id="demo-wf",
        name="Demo Workflow",
        description="Tests plugin and fs",
        steps=[
            Step(id="step1", request=CapabilityRequest(id="hello_world", parameters={"name": "ATLAS User"})),
            Step(id="step2", request=CapabilityRequest(id="filesystem", parameters={"operation": "write", "path": "demo_output.txt", "content": "Success!"}))
        ]
    )
    
    success = wf_engine.execute(wf)
    print(f"    Workflow execution success: {success}")
    
    print("\n[*] System Recording (Ledger History):")
    history = ledger.get_history()
    for event in history:
        print(f"[{event.timestamp.strftime('%H:%M:%S')}] {event.type.upper()} - {event.payload}")

if __name__ == '__main__':
    main()
