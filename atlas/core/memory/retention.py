from datetime import timedelta
from typing import Optional
from .store import Fact, _now_utc

class RetentionManager:
    def __init__(self, default_ttl_days: Optional[int] = None):
        self.default_ttl_days = default_ttl_days

    def apply_policy(self, fact: Fact):
        if not fact.expires_at and self.default_ttl_days is not None:
            fact.expires_at = _now_utc() + timedelta(days=self.default_ttl_days)
