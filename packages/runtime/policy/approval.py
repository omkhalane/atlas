"""
Resumable Approval Manager
Decouples human approval into a resumable state. Workflow pauses in WAITING state until user approval.
"""
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger("atlas.policy.approval")


@dataclass
class ApprovalRequest:
    id: str
    task_id: str
    action: str
    reason: str
    status: str = "pending"         # "pending" | "approved" | "rejected"
    requested_at: float = field(default_factory=time.time)
    decision_at: Optional[float] = None


class ResumableApprovalManager:
    def __init__(self):
        self._requests: Dict[str, ApprovalRequest] = {}

    def request_approval(self, task_id: str, action: str, reason: str) -> ApprovalRequest:
        req_id = f"appr_{task_id}_{int(time.time())}"
        req = ApprovalRequest(id=req_id, task_id=task_id, action=action, reason=reason)
        self._requests[req_id] = req
        logger.info(f"Created approval request {req_id} for task {task_id}: {reason}")
        return req

    def approve(self, request_id: str) -> bool:
        req = self._requests.get(request_id)
        if req:
            req.status = "approved"
            req.decision_at = time.time()
            logger.info(f"Approved request {request_id}")
            return True
        return False

    def reject(self, request_id: str) -> bool:
        req = self._requests.get(request_id)
        if req:
            req.status = "rejected"
            req.decision_at = time.time()
            logger.info(f"Rejected request {request_id}")
            return True
        return False

    def get_pending_approvals(self) -> List[ApprovalRequest]:
        return [r for r in self._requests.values() if r.status == "pending"]
