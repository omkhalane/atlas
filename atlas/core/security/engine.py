from atlas.core.contracts import PermissionRequest, PolicyDecision

class SecurityEngine:
    def __init__(self):
        self.default_policy = PolicyDecision(
            allowed=False, 
            explanation="Default deny policy enforces safety by blocking unconfigured mutations."
        )

    def authorize(self, request: PermissionRequest) -> PolicyDecision:
        # For Phase 0, we simply enforce the default deny policy.
        return self.default_policy
