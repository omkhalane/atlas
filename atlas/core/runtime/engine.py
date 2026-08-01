from atlas.core.contracts import Plan, Event, PermissionRequest
from atlas.core.capabilities.engine import CapabilityEngine
from atlas.core.security import SecurityEngine
from atlas.core.runtime.validator import Validator
from atlas.core.runtime.ledger import TransactionLedger
from atlas.core.runtime.verifier import Verifier
import uuid

class Runtime:
    def __init__(self, 
                 capability_engine: CapabilityEngine, 
                 security_engine: SecurityEngine,
                 ledger: TransactionLedger,
                 validator: Validator,
                 verifier: Verifier):
        self.capability_engine = capability_engine
        self.security_engine = security_engine
        self.ledger = ledger
        self.validator = validator
        self.verifier = verifier

    def execute(self, plan: Plan) -> bool:
        # 1. Validate
        val_result = self.validator.validate(plan)
        if not val_result.valid:
            self._log_event(plan.id, "plan_failed", {"error": val_result.error})
            return False

        self._log_event(plan.id, "plan_started", {"steps": len(plan.steps)})

        # 2. Execute steps
        for step in plan.steps:
            self._log_event(plan.id, "step_started", {"step_id": step.id})
            
            # Request permission
            manifest = self.capability_engine.get_manifest(step.request.id)
            for perm in manifest.required_permissions:
                decision = self.security_engine.authorize(
                    PermissionRequest(capability_id=step.request.id, scope=perm, reason="Plan execution")
                )
                if not decision.allowed:
                    err = f"Permission denied for {perm}: {decision.explanation}"
                    self._log_event(plan.id, "step_failed", {"step_id": step.id, "error": err})
                    return False
            
            # Execute
            result = self.capability_engine.execute(step.request)
            if not result.success:
                self._log_event(plan.id, "step_failed", {"step_id": step.id, "error": result.error})
                return False
                
            # Verify
            ver_result = self.verifier.verify(step, result)
            if not ver_result.verified:
                self._log_event(plan.id, "step_verification_failed", {"step_id": step.id, "error": ver_result.error})
                return False
                
            self._log_event(plan.id, "step_completed", {"step_id": step.id, "data": result.data})

        self._log_event(plan.id, "plan_completed", {})
        return True

    def _log_event(self, plan_id: str, type: str, payload: dict):
        payload["plan_id"] = plan_id
        event = Event(id=str(uuid.uuid4()), type=type, payload=payload)
        self.ledger.append(event)
