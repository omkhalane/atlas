import os
import json
from typing import Dict, Any

class AuthenticationManager:
    def __init__(self, data_file: str = ".atlas/auth.json"):
        self.data_file = data_file
        self.credentials: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, 'r') as f:
                self.credentials = json.load(f)
        except Exception:
            self.credentials = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        # Note: In a real production system, this should use OS secure storage (Keychain/Keyring)
        with open(self.data_file, 'w') as f:
            json.dump(self.credentials, f, indent=2)

    def store_credentials(self, provider_id: str, auth_data: Dict[str, Any]):
        self.credentials[provider_id] = auth_data
        self._save()

    def get_credentials(self, provider_id: str) -> Dict[str, Any]:
        return self.credentials.get(provider_id, {})

    def clear_credentials(self, provider_id: str):
        if provider_id in self.credentials:
            del self.credentials[provider_id]
            self._save()

manager = AuthenticationManager()
