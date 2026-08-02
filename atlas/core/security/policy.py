from atlas.core.contracts.security import PermissionRequest, PolicyDecision

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
        if cid in self.high_risk_actions and action in self.high_risk_actions[cid]:
            # If the request parameters already explicitly say approved=True, allow it
            if request.parameters.get("approved") is True:
                return PolicyDecision(allowed=True, requires_human=False, explanation="Action approved by user.")
                
            return PolicyDecision(
                allowed=False, 
                requires_human=True, 
                explanation=f"Action '{action}' on capability '{cid}' is high risk and requires human approval."
            )
            
        return PolicyDecision(allowed=True, requires_human=False, explanation="Action is low risk.")
