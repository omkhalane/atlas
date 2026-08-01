from atlas.core.contracts import CapabilityResult, Step

class VerificationResult:
    def __init__(self, verified: bool, error: str = None):
        self.verified = verified
        self.error = error

class Verifier:
    def verify(self, step: Step, result: CapabilityResult) -> VerificationResult:
        if result.success:
            return VerificationResult(True)
        else:
            return VerificationResult(False, result.error)
