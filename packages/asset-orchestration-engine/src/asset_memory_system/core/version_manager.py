import hashlib
import json
from typing import Dict, Any, Optional

class VersionManager:
    @staticmethod
    def calculate_parameter_hash(parameters: Dict[str, Any], template_version: str = "1.0.0") -> str:
        data = {"params": parameters, "tpl_ver": template_version}
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def bump_version(current_version: str, bump_type: str = "PATCH") -> str:
        parts = [int(p) for p in current_version.split(".")]
        if bump_type == "MAJOR":
            parts[0] += 1
            parts[1] = 0
            parts[2] = 0
        elif bump_type == "MINOR":
            parts[1] += 1
            parts[2] = 0
        else: # PATCH
            parts[2] += 1
        return ".".join(str(p) for p in parts)
