import os
import json
from typing import Dict, List, Set

class PermissionManager:
    def __init__(self, data_file: str = ".atlas/permissions.json"):
        self.data_file = data_file
        self.granted_permissions: Dict[str, Set[str]] = {} # provider_id -> set of capability/permission ids
        self._load()

    def _load(self):
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.granted_permissions = {k: set(v) for k, v in data.items()}
        except Exception:
            self.granted_permissions = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump({k: list(v) for k, v in self.granted_permissions.items()}, f, indent=2)

    def grant(self, provider_id: str, permission_id: str):
        if provider_id not in self.granted_permissions:
            self.granted_permissions[provider_id] = set()
        self.granted_permissions[provider_id].add(permission_id)
        self._save()

    def revoke(self, provider_id: str, permission_id: str):
        if provider_id in self.granted_permissions:
            self.granted_permissions[provider_id].discard(permission_id)
            self._save()

    def has_permission(self, provider_id: str, permission_id: str) -> bool:
        return permission_id in self.granted_permissions.get(provider_id, set())

    def get_granted(self, provider_id: str) -> List[str]:
        return list(self.granted_permissions.get(provider_id, set()))

manager = PermissionManager()
