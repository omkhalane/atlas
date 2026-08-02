from runtime.contracts.security import PermissionRequest, PolicyDecision

class PolicyEngine:
    def __init__(self):
        # Define high risk actions that require human approval
        self.high_risk_actions = {
            "filesystem": ["delete_file"],
            "command": ["run"], # arbitrary commands are high risk
            "browser": [] 
        }

    def evaluate(self, request: PermissionRequest) -> PolicyDecision:
        cid = request.capability_id
        action = request.action
        
        # Check if the capability and action are in the high-risk registry
        # Auto approve all actions as requested by user
        if cid in self.high_risk_actions and action in self.high_risk_actions[cid]:
            return PolicyDecision(
                allowed=True, 
                requires_human=False, 
                explanation=f"Auto-approved high risk action '{action}' on capability '{cid}'."
            )
            
        return PolicyDecision(allowed=True, requires_human=False, explanation="Action is low risk.")
