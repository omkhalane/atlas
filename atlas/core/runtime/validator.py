from atlas.core.contracts import Plan
from atlas.core.capabilities.engine import CapabilityEngine

class ValidationResult:
    def __init__(self, valid: bool, error: str = None):
        self.valid = valid
        self.error = error

class Validator:
    def __init__(self, capability_engine: CapabilityEngine):
        self.capability_engine = capability_engine

    def validate(self, plan: Plan) -> ValidationResult:
        step_ids = set()
        
        for step in plan.steps:
            if step.id in step_ids:
                return ValidationResult(False, f"Duplicate step ID '{step.id}' found.")
            step_ids.add(step.id)

            manifest = self.capability_engine.get_manifest(step.request.id)
            if not manifest:
                return ValidationResult(False, f"Step '{step.id}' uses unknown capability '{step.request.id}'.")
            
            provided_params = set(step.request.parameters.keys())
            required_params = {p.name for p in manifest.parameters if p.required}
            missing = required_params - provided_params
            if missing:
                return ValidationResult(False, f"Step '{step.id}' missing required parameters: {missing}")

            for dep in step.dependencies:
                if dep not in step_ids:
                    return ValidationResult(False, f"Step '{step.id}' depends on missing or future step '{dep}'.")

        return ValidationResult(True)
