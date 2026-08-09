from runtime.contracts.security import PermissionRequest, PolicyDecision

class PolicyEngine:
    def __init__(self):
        # Define high risk actions that require human approval
        self.high_risk_actions = {
            "filesystem": ["write_file", "delete_file"],
            "command": ["run"],
            "mcp_chrome-devtools": ["navigate_page"]
        }

    def evaluate(self, request: PermissionRequest) -> PolicyDecision:
        cid = request.capability_id
        action = request.action
        
        # Check if the capability and action are in the high-risk registry
        if cid in self.high_risk_actions and action in self.high_risk_actions[cid]:
            return PolicyDecision(
                allowed=False, 
                requires_human=True, 
                explanation=f"Action '{action}' on capability '{cid}' requires human approval."
            )
            
        return PolicyDecision(allowed=True, requires_human=False, explanation="Action is low risk.")
