import re
from typing import Dict, Any

class SensitivityFilter:
    def __init__(self):
        self.patterns = [
            (re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'), '[REDACTED_EMAIL]'),
            (re.compile(r'\b(?:\d[ -]*?){13,16}\b'), '[REDACTED_CARD]')
        ]

    def filter_text(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        result = text
        for pattern, replacement in self.patterns:
            result = pattern.sub(replacement, result)
        return result

    def filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in data.items():
            if isinstance(v, str):
                result[k] = self.filter_text(v)
            elif isinstance(v, dict):
                result[k] = self.filter_dict(v)
            elif isinstance(v, list):
                result[k] = [self.filter_text(item) if isinstance(item, str) else item for item in v]
            else:
                result[k] = v
        return result
