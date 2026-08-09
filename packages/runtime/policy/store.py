"""
SessionPolicyRegistry — maps session_id → permitted tool scopes.

Fail-closed defaults:
  - Unknown sessions receive SAFE only.
  - Explicit grants required for READ/WRITE/BROWSER/NETWORK/DANGEROUS.

Import namespace: runtime.policy.store
"""
from __future__ import annotations

import logging
from typing import Dict, Set, List

logger = logging.getLogger("atlas.policy.store")

_DEFAULT_SCOPES: Set[str] = {"SAFE"}


class SessionPolicyRegistry:
    """
    In-memory policy store. One entry per session_id.
    Grants are additive — remove by revoking the entire session entry.
    """

    def __init__(self) -> None:
        self._grants: Dict[str, Set[str]] = {}

    def grant(self, session_id: str, scopes: List[str]) -> None:
        if session_id not in self._grants:
            self._grants[session_id] = set(_DEFAULT_SCOPES)
        self._grants[session_id].update(scopes)
        logger.info(f"PolicyStore: grant session={session_id!r} scopes={scopes}")

    def revoke(self, session_id: str) -> None:
        self._grants.pop(session_id, None)

    def get_permitted_scopes(self, session_id: str) -> Set[str]:
        return self._grants.get(session_id, _DEFAULT_SCOPES)
