import pytest
from atlas.core.contracts import CapabilityRequest, Step
from atlas.core.workflows.schema import Workflow
from atlas.core.workflows.engine import WorkflowEngine
from atlas.core.capabilities.engine import CapabilityEngine
from atlas.core.capabilities.manifest import CapabilityManifest
from atlas.core.security.engine import SecurityEngine
from atlas.core.runtime.validator import Validator
from atlas.core.runtime.ledger import SQLiteLedger
from atlas.core.runtime.verifier import Verifier
from atlas.core.runtime.engine import Runtime
from tests.fixtures.fake_adapters import FakeProcessPort

def test_workflow_execution():
    capability_engine = CapabilityEngine()
    manifest = CapabilityManifest(
        id="proc",
        description="Run process",
        version="1.0.0",
        parameters=[],
        required_permissions=[]
    )
    capability_engine.register(manifest, FakeProcessPort())
    
    runtime = Runtime(
        capability_engine=capability_engine,
        security_engine=SecurityEngine(),
        ledger=SQLiteLedger(":memory:"),
        validator=Validator(capability_engine),
        verifier=Verifier()
    )
    
    workflow_engine = WorkflowEngine(runtime)
    
    step1 = Step(
        id="step-1",
        request=CapabilityRequest(id="proc", parameters={"command": "echo test"})
    )
    workflow = Workflow(id="wf-1", name="Test WF", description="Test", steps=[step1])
    
    success = workflow_engine.execute(workflow)
    assert success is True
    
    history = runtime.ledger.get_history()
    event_types = [e.type for e in history]
    assert "plan_started" in event_types
    assert "step_completed" in event_types
