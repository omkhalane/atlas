import pytest
from atlas.core.contracts import Plan, Step, CapabilityRequest
from atlas.core.capabilities.engine import CapabilityEngine
from atlas.core.capabilities.manifest import CapabilityManifest, CapabilityParameter
from atlas.core.security.engine import SecurityEngine
from atlas.core.runtime.validator import Validator
from atlas.core.runtime.ledger import SQLiteLedger
from atlas.core.runtime.verifier import Verifier
from atlas.core.runtime.engine import Runtime
from tests.fixtures.fake_adapters import FakeFilesystemPort

@pytest.fixture
def capability_engine():
    engine = CapabilityEngine()
    manifest = CapabilityManifest(
        id="fs_read",
        description="Reads a file",
        version="1.0.0",
        parameters=[
            CapabilityParameter(name="operation", type="str", description="operation"),
            CapabilityParameter(name="path", type="str", description="file path")
        ],
        required_permissions=[]
    )
    engine.register(manifest, FakeFilesystemPort())
    return engine

@pytest.fixture
def runtime(capability_engine):
    return Runtime(
        capability_engine=capability_engine,
        security_engine=SecurityEngine(),
        ledger=SQLiteLedger(":memory:"),
        validator=Validator(capability_engine),
        verifier=Verifier()
    )

def test_runtime_execution(runtime, capability_engine):
    fs = capability_engine._adapters["fs_read"]
    fs.files["/tmp/test.txt"] = "hello world"

    step1 = Step(
        id="step-1",
        request=CapabilityRequest(id="fs_read", parameters={"operation": "read", "path": "/tmp/test.txt"})
    )
    plan = Plan(id="plan-1", steps=[step1])

    success = runtime.execute(plan)
    assert success is True

    history = runtime.ledger.get_history()
    event_types = [e.type for e in history]
    assert "plan_started" in event_types
    assert "step_completed" in event_types
    assert "plan_completed" in event_types
