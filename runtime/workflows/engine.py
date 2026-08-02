import uuid
from typing import Dict, Any
from runtime.contracts import Plan
from runtime.workflows.schema import Workflow
from runtime.kernel.engine import Runtime

class WorkflowEngine:
    def __init__(self, runtime: Runtime):
        self.runtime = runtime

    def compile(self, workflow: Workflow, inputs: Dict[str, Any] = None) -> Plan:
        plan_id = f"plan-{uuid.uuid4()}"
        
        # A more advanced compiler would substitute parameters using inputs.
        # For this prototype, we just pass the steps directly to the plan.
        return Plan(id=plan_id, steps=workflow.steps)

    def execute(self, workflow: Workflow, inputs: Dict[str, Any] = None) -> bool:
        plan = self.compile(workflow, inputs)
        return self.runtime.execute(plan)
