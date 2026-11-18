from typing import Dict, Optional

class ParameterMappingEngine:
    MAPPINGS: Dict[str, str] = {
        "blade_too_narrow": "blade_width",
        "blade_too_wide": "blade_width",
        "blade_too_short": "blade_length",
        "blade_too_long": "blade_length",
        "handle_too_short": "handle_length",
        "handle_too_long": "handle_length",
        "guard_too_narrow": "guard_width",
        "guard_too_wide": "guard_width",
        "pommel_too_small": "pommel_size",
        "pommel_too_large": "pommel_size"
    }

    @classmethod
    def map_issue_to_parameter(cls, issue_key: str) -> Optional[str]:
        return cls.MAPPINGS.get(issue_key.lower())
