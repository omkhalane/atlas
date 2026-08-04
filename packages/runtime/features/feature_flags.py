"""
Feature Flags Engine
Dynamic runtime toggles for features like prompt cache, reasoning models, vision, planning, etc.
"""
from typing import Dict, Any


class FeatureFlags:
    def __init__(self):
        self._flags: Dict[str, bool] = {
            "prompt_caching": True,
            "reasoning_models": True,
            "vision": True,
            "browser_tools": True,
            "mcp_servers": True,
            "background_summarizer": True,
            "strict_token_budgeting": True,
        }

    def is_enabled(self, feature: str) -> bool:
        return self._flags.get(feature, False)

    def set_flag(self, feature: str, enabled: bool):
        self._flags[feature] = enabled

    def get_all_flags(self) -> Dict[str, bool]:
        return dict(self._flags)
